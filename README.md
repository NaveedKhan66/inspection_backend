# Construction Project Management System

This system is a comprehensive solution for managing construction projects, designed to streamline communication and workflows between builders, homeowners, trades, and administrators.

## Overview

The Construction Project Management System facilitates:

- Project creation and management by administrators
- Builder and homeowner assignment to projects
- Multiple inspection processes for quality control
- Deficiency tracking and assignment to relevant trades
- Image uploads for deficiencies and blueprints
- Automated inspection reporting
- Multiple dashboards for different user roles

## Technology Stack

- Backend: Django (Python)
- Frontend: React
- Database: PostgreSQL
- Deployment:
  - Frontend: AWS CloudFront
  - Backend: AWS Elastic Beanstalk
- Email Service: AWS SES (Simple Email Service)

## Backend Setup

To set up the backend locally, follow these steps:

1. Clone the repository:
   ```
   git clone [repository-url]
   cd [project-directory]
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Get the env file from the developer and place it in the directory `inspections_backend/`

5. If you want to connect a local database, create the database first and then run migrations

6. Run migrations:
   ```
   python manage.py migrate
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## Database connections:
You can connect to the staging and production database locally by using the database credentials present
in the .env file.

## Deployment Information

The system is deployed using the following AWS services:

- Frontend: AWS CloudFront
  - Provides fast content delivery and HTTPS support

- Backend: AWS Elastic Beanstalk
  - Manages the deployment, scaling, and health monitoring of the Django application

- Database: Amazon RDS (PostgreSQL)
  - Provides a managed PostgreSQL database service

- Email: Amazon SES
  - Handles all transactional emails sent by the system

## Deployment Steps:

1. Make sure the .env file is present in the `inspections_backend/` directory.
2. Navigate to the root directory of the project.
3. Run the command
```
   eb init -i
```
This command will initialize the project.
4. Select the region ca-central-1 where both the environments are present
5. Don't use code commit
6. Python version 3.11 is used
7. Staging environment name: eagle-eye-Inspection-stagging-env
8. Production environment name: Inspectionapplication-staging-env
9. In future you can change the environment by using following commands
```
eb list
```
this will list all the environments
10. eb use <environment-name>. This will set the environment as default environment
2. Run the following command to deploy the application. Only this command can be used in future
to deploy the application if the setup is done:
   ```
   eb deploy
   ```

## API Documentation

API documentation is available at the following endpoints:

- Swagger UI: `/api/schema/swagger`
- ReDoc: `/api/schema/redoc`

These endpoints provide interactive documentation for all available API endpoints, including request/response schemas and example usage.
