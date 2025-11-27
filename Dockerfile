# Use Python 3.11 slim image (more up-to-date and compatible with local environment)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application and bind to Render's $PORT (default to 5000 if not set)
# Use 'sh -c' so environment variable expansion works when Docker runs the CMD.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --timeout 120 --workers 2 --threads 4 app:app"]
