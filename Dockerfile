# Use an official Python runtime based on Python 3.12-slim
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache for dependencies
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variables for database URL and secret key (can be set dynamically in ECS)
ENV DATABASE_URL=$DATABASE_URL
ENV SECRET_KEY=$SECRET_KEY

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
