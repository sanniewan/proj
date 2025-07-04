# FROM arm64v8/ros:humble-ros-base-jammy

# # System dependencies
# RUN apt-get update && \
#     apt-get install -y \
#         python3-pip \
#         python3-dev \
#         i2c-tools \
#         libgpiod-dev \
#         && rm -rf /var/lib/apt/lists/*

# # Python libraries for GPIO and I2C
# RUN pip3 install --no-cache-dir \
#     adafruit-blinka \
#     adafruit_ahtx0
#     RPi.GPIO \
#     lgpio \
#     setuptools==58.2.0

# # Set working directory to your project
# WORKDIR /workspace/proj

# # Copy your project into the container
# COPY . .

# # Start with bash so you can manually run scripts
# CMD ["/bin/bash"]



FROM arm64v8/ros:humble-ros-base-jammy

# System dependencies
RUN apt-get update && \
    apt-get install -y \
        python3-pip \
        python3-dev \
        i2c-tools \
        libgpiod-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt into the image
COPY ./docker/requirements.txt /tmp/requirements.txt

# Install Python dependencies
ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN pip3 install --upgrade pip && \
    pip3 install -r /tmp/requirements.txt

# Set working directory to your project
WORKDIR /workspace/proj

# Copy your project into the container
COPY . .

# Install the local package
RUN pip3 install -e .

CMD ["/bin/bash"]

# FROM arm64v8/ros:humble-ros-base-jammy

# # Optional, if using build backend
# RUN pip3 install --upgrade pip setuptools && \
#     pip3 install -e .

# # Install your project + dependencies
# COPY . /workspace/proj

# # Set working directory to your project
# WORKDIR /workspace/proj

# CMD ["/bin/bash"]