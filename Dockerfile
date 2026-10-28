# Use an explicit, slim Python base image to guarantee version lock-in
FROM python:3.12-slim

# Set environment variables to keep Python well-behaved in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /code

# Install system dependencies needed for compiling tools or running health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade build tools and guarantee setuptools is available for legacy dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir "setuptools<82.0.0"

# Leverage Docker's layer caching by copying only requirements first
COPY ./requirements/prod.txt /code/requirements.txt

# Install the exact package versions safely on Python 3.12
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the rest of the application code
COPY . /code/
