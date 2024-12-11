# User Profile Service

This service is designed to handle and manage user profiles within our application. It allows users to view and update their profile information, including their name, resume, job applications, and job recommendations.

## Responsibilities

- **User Profile Management**: Users can view their profile details, including their name and resume URL.
- **Resume Handling**: Users can view and update their resume URL directly from their profile.
- **Preference Handling**: Users can view and update their job preferences, including but not limited to location, job type, etc.

## FastAPI

This service is built using **FastAPI**, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

Key features of FastAPI used in this service:
- **Asynchronous Request Handling**: FastAPI handles requests asynchronously, ensuring high performance even with many concurrent requests.
- **Automatic Validation**: Input validation is automatically handled using Pydantic models, ensuring data integrity.
- **OpenAPI Documentation**: FastAPI generates automatic interactive API documentation using Swagger UI, making it easy to interact with the API endpoints and test them.

## Deployment

The service is deployed in a cloud-based environment on AWS ECS. This service is part of the Stay Employed App.
