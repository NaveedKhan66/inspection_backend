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
   Create a `.env` file in the project root and add the following variables:
   ```
   DEBUG=True
   SECRET_KEY=[your-secret-key]
   DATABASE_URL=[your-database-url]
   AWS_ACCESS_KEY_ID=[your-aws-access-key]
   AWS_SECRET_ACCESS_KEY=[your-aws-secret-key]
   AWS_SES_REGION_NAME=[your-aws-region]
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

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

## API Documentation

API documentation is available at the following endpoints:

- Swagger UI: `/api/schema/swagger`
- ReDoc: `/api/schema/redoc`

These endpoints provide interactive documentation for all available API endpoints, including request/response schemas and example usage.
