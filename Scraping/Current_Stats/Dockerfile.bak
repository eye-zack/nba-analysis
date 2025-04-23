# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV key="PYTHONDONTWRITEBYTECODE 1"
ENV key="PYTHONUNBUFFERED 1"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY nba_scraper.py .

# Set the entrypoint
CMD ["python", "nba_scraper.py"]