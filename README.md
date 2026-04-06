# KanMind Backend

Backend project for the KanMind application built with Django and Django REST Framework.

## Setup

1. Create virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Run server:
   python manage.py runserver

## Tech Stack

- Django
- Django REST Framework

## Current Project Structure

The backend project was initialized with Django and Django REST Framework.

Current setup includes:

- core project configuration
- app structure for authentication, boards and tasks
- dedicated API folders inside each app for serializers, views and URL configuration

## Current Project Status

The backend base setup has been further extended with a modular API routing structure.

Current progress includes:

- integration of token authentication using Django REST Framework
- CORS configuration for local frontend-backend communication
- centralized root URL configuration in `core/urls.py`
- initial API endpoint structure based on the provided documentation
