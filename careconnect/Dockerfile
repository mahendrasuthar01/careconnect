# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Create a directory for media files
RUN mkdir -p /app/media && chmod -R 755 /app/media

# Install system dependencies required for the application
RUN apt update && apt install -y build-essential

# Copy requirements.txt into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Collect static files (this assumes STATIC_ROOT is set in your settings.py)
RUN python manage.py collectstatic --noinput

# Expose port 8000 to be accessible outside the container
EXPOSE 8000

# Define the default command to run your application with Gunicorn
CMD ["uvicorn", "careconnect.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

