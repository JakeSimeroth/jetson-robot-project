# Dockerfile for Jetson Robot Project
FROM nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libopencv-dev \
    pkg-config \
    cmake \
    build-essential \
    git \
    curl \
    wget \
    nano \
    htop \
    v4l-utils \
    i2c-tools \
    gpio \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install additional Jetson-specific packages
RUN pip3 install --no-cache-dir \
    jetson-stats \
    jetson-gpio

# Copy project files
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY hello_jetson.py .

# Set permissions for GPIO access
RUN groupadd -f gpio && \
    usermod -a -G gpio root

# Create logs directory
RUN mkdir -p logs

# Set up entry point
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports for web interface (if needed)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import cv2; print('OK')" || exit 1

# Default command
CMD ["/entrypoint.sh"]