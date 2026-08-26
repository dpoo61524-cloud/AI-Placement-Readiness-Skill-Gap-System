# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies (needed for compiling certain native packages if required)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source directories and assets
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/
COPY backend/ ./backend/

# Expose port
EXPOSE 8000

# Start FastAPI application
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
