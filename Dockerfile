FROM ubuntu:jammy 
WORKDIR /srv

# Build stage: Install yarn dependencies
# ===
FROM node:20 AS yarn-dependencies
WORKDIR /srv
RUN export NODE_ENV=docker
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
ADD . .
RUN yarn run build-css

# Build the production image
# ===
FROM ubuntu:jammy

# Set up environment
ENV LANG C.UTF-8
WORKDIR /srv
COPY . .

# Install python and import python dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes python3-pip python3-lib2to3 python3-setuptools python3-pkg-resources ca-certificates libsodium-dev
RUN pip install -r requirements.txt


# Import code, build assets
RUN rm -rf package.json yarn.lock vite.config.js requirements.txt
COPY --from=build-css /srv/static/build/styles.css /srv/static/build/styles.css
COPY --from=build-js /srv/static/build /srv/static/build

# Set build ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"

# Setup commands to run web service
ENTRYPOINT ["./entrypoint"]
CMD ["0.0.0.0:80"]
