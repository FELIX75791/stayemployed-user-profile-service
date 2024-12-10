# Use an official Python runtime as a parent image
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

# Command to run the FastAPI app using Uvicorn, correct path is app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
