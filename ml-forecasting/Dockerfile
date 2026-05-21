# Dockerfile — Module 2: LSTM Forecasting API
FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create dirs
RUN mkdir -p models outputs/charts data

EXPOSE 5001

# Start Flask API (models must be pre-trained and mounted via volume)
CMD ["python", "app.py"]
