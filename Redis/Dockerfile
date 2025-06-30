# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# For Greek timezone
RUN apt-get update && apt-get install -y tzdata 

# Expose Flask default port
EXPOSE 5000

# Run Flask app
CMD ["python", "-m", "src.app"]
