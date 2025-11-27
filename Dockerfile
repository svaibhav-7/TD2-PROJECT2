# Use Python 3.11 slim image (more up-to-date and compatible with local environment)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# No special system dependencies are required because the Playwright base image
# already provides the necessary browsers and libraries.

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application and bind to Render's $PORT (default to 5000 if not set)
# Use 'sh -c' so environment variable expansion works when Docker runs the CMD.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --timeout 120 --workers 2 --threads 4 app:app"]
