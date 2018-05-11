#!/bin/bash

PACKAGES=(
)

DEV_PACKAGES=(
  gcc
  musl-dev
)

apk add --update --no-cache ${PACKAGES[@]}
apk add --no-cache --virtual .build-dependencies ${DEV_PACKAGES[@]}
