# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file in the container
COPY ../requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from src
COPY ../src/app.py .
#COPY ../src/users.json .

# Expose the port your app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
