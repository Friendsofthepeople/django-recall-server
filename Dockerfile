# Dockerfile
# FROM python:3.10-slim

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# Set work directory
# WORKDIR /code

# Install dependencies
# COPY requirements/prod.txt /code/requirements/prod.txt
# RUN pip install --no-cache-dir -r requirements/prod.txt

# RUN python manage.py collectstatic --noinput 

# EXPOSE 8000

# Copy project
# COPY . /code/

# RUN chmod +x /code/entrypoint.sh

# ENTRYPOINT ["./entrypoint.sh"]


FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements/prod.txt /code/requirements/prod.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

EXPOSE 8000

# Copy project
COPY . /code/