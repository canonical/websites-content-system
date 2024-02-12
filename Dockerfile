FROM ubuntu:jammy 
WORKDIR /srv

# Build stage: Install python dependencies
# ===
RUN apt-get update && apt-get install --no-install-recommends --yes git python3-pip python3-setuptools
COPY . .
RUN pip3 config set global.disable-pip-version-check true
RUN pip3 install -r requirements.txt

# Set build ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"
