#!/bin/bash

docker run -it --privileged \
  --device /dev/i2c-1 \
  -v ~/proj:/workspace/proj \
  proj