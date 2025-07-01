#!/bin/bash

# Build Docker image for Proj
docker build \
    --no-cache \
    -t proj \
    -f ./Dockerfile \
    ..
