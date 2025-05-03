# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (including ffmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
# Assuming your application code is inside the 'project' directory
COPY ./project ./project

# Expose the port the app runs on
EXPOSE 8000

# Set environment variable for allowed origins (can be overridden at runtime)
# Provide a sensible default for local development if not set
ENV ALLOWED_ORIGINS="http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000"

# Define the command to run the application
# Use 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "project.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
