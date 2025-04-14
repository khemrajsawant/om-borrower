# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the contents of the local directory to the container
COPY . /app

# Install system dependencies (optional but recommended for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r package_requirements.txt

# Expose port (optional: change this according to your app)
EXPOSE 5000

# Command to run the application
CMD ["python", "run.py"]
