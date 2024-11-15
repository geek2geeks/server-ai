# Location: E:/justica/docker/Dockerfile

FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="8.6" \
    FORCE_CUDA="1" \
    PATH="/usr/local/bin:${PATH}" \
    PYTHON_PATH="/usr/bin/python3"

# Install system dependencies including OpenCV requirements
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    ffmpeg \
    libx264-dev \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir setuptools wheel && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 -m pip install --no-cache-dir prometheus_client && \
    rm -rf /root/.cache/pip/*

# Copy application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import torch; assert torch.cuda.is_available()"

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python3", "-m", "src.api.unified_server"]