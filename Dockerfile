# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for OpenCV, Dlib, and audio processing
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    ffmpeg \
    libsm6 \
    libxext6 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# We use standard webrtcvad on Linux (webrtcvad-wheels is Windows-only)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir resemblyzer --no-deps

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
