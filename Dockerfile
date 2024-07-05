FROM ubuntu:jammy 
WORKDIR /srv

# Build stage: Install python dependencies
# ===
RUN apt-get update && apt-get install --no-install-recommends --yes git python3-pip python3-setuptools
COPY . .
RUN pip3 config set global.disable-pip-version-check true
RUN pip3 install -r requirements.txt

# Build stage: Install yarn dependencies
# ===
FROM node:19 AS yarn-dependencies
WORKDIR /srv
ADD yarn.lock .
ADD package.json .
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn yarn install


# Build stage: Build js
# ===
FROM yarn-dependencies AS build-js
ADD . .
RUN yarn run build-js

# Build stage: Build CSS
# ===
FROM yarn-dependencies AS build-css
RUN yarn run build-css

# Build the production image
# ===
FROM ubuntu:jammy

# Install python and import python dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes python3-lib2to3 python3-setuptools python3-pkg-resources ca-certificates libsodium-dev
ENV PATH="/root/.local/bin:${PATH}"

# Copy python dependencies
COPY --from=python-dependencies /root/.local/lib/python3.8/site-packages /root/.local/lib/python3.8/site-packages
COPY --from=python-dependencies /root/.local/bin /root/.local/bin

# Set up environment
ENV LANG C.UTF-8
WORKDIR /srv

# Import code, build assets
COPY . .
RUN rm -rf package.json yarn.lock vite.config.js requirements.txt
COPY --from=build-css /srv/static/css static/css
COPY --from=build-js /srv/static/js static/js
COPY --from=build-js /srv/static/dist static/dist

# Set build ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"

# Setup commands to run web service
ENTRYPOINT ["./entrypoint"]
CMD ["0.0.0.0:80"]
