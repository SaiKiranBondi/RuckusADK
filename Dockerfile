FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT=ruckusdevtools

# Run the ADK-based web interface
CMD ["python", "web_interface_adk.py"]
