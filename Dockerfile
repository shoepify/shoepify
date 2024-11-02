# Dockerfile
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Django project files
COPY . .

# Run migrations and start the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
