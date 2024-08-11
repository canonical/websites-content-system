FROM ubuntu:jammy 
WORKDIR /srv

# Build stage: Build static files
# ===
FROM node:20 AS build
WORKDIR /srv
ADD . .
RUN export NODE_ENV=docker
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn yarn install
RUN yarn build

# Build the production image
# ===
FROM ubuntu:jammy

# Set up environment
ENV LANG C.UTF-8
WORKDIR /srv
COPY . .

# Install python and import python dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes python3-pip ca-certificates git
RUN pip install -r requirements.txt

# Import code, build assets
RUN rm -rf package.json yarn.lock vite.config.js requirements.txt
COPY --from=build /srv/static/build /srv/static/build

# Set build ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"

# Setup commands to run web service
ENTRYPOINT ["./entrypoint"]
CMD ["0.0.0.0:80"]
