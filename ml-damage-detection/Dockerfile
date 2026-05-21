# Dockerfile — Module 3: CNN Damage Detection API
FROM python:3.11-slim

WORKDIR /app

# System dependencies (OpenCV needs libGL)
RUN apt-get update && apt-get install -y \
    curl libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Ensure artifact dirs exist
RUN mkdir -p models outputs/charts outputs/predictions data/train data/val data/test

EXPOSE 5002

# Flask API — expects best_model.keras to be in /app/models (mounted via volume)
CMD ["python", "app.py"]
