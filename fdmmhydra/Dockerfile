# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /fdmmhydra
COPY requirements.txt /fdmmhydra

RUN apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers \
    bash \
    curl \
    docker-cli \
    docker-compose \
    && pip install docker

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt
    
COPY . /fdmmhydra

ENTRYPOINT ["python3", "-u", "app.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
