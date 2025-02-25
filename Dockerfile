# Use official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Start the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
