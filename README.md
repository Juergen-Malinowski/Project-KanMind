# KanMind Backend

Backend project for the KanMind application built with Django and Django REST Framework.

## Setup

Run the following commands to set up the project locally:

```bash
# Clone repository
git clone <your-repository-url>
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux / Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template (Windows)
copy .env.template .env

# Create .env file from template (Linux / Mac)
cp .env.template .env

# Generate a new Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Open .env and insert your SECRET_KEY

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## API Routing Overview

The API routing has been fully structured according to the provided documentation and aligned with the frontend configuration.

The following endpoints are prepared:

- Authentication:
  - /api/registration/
  - /api/login/
  - /api/email-check/

- Boards:
  - /api/boards/
  - /api/boards/{board_id}/

- Tasks:
  - /api/tasks/
  - /api/tasks/assigned-to-me/
  - /api/tasks/reviewing/
  - /api/tasks/{task_id}/
  - /api/tasks/{task_id}/comments/
  - /api/tasks/{task_id}/comments/{comment_id}/

All routes are organized in a modular structure using app-specific API modules and centralized routing via `core/urls.py`.

## Tech Stack

- Django
- Django REST Framework

## Current Project Structure

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

## Environment Setup

This project uses environment variables to securely manage sensitive data such as the Django `SECRET_KEY`.

### Setup instructions

After cloning the repository, you must create your own `.env` file in the project root directory.

1. Copy the provided `.env.template` file
2. Rename it to `.env`
3. Insert your own generated Django `SECRET_KEY`

Example:

```env
SECRET_KEY=your_secret_key_here
```

If your key contains special characters such as `#`, use double quotes:

```env
SECRET_KEY="your_secret_key_here"
```

Important:

- The `.env` file must never be committed to the repository
- Each developer must generate their own `SECRET_KEY`
- If a `SECRET_KEY` was exposed, it must be replaced immediately

## Custom User Model

This project uses a custom user model based on Django’s `AbstractBaseUser` and `PermissionsMixin`.

### Key characteristics

- Authentication is based on `email` instead of a username
- A `fullname` field is used instead of separate first and last names
- The default Django user model is fully replaced via:

```env
AUTH_USER_MODEL = "auth_app.User"
```

### Implementation details

- `AbstractBaseUser` handles authentication (password, login)
- `PermissionsMixin` provides authorization (roles, permissions, superuser)
- A custom `UserManager` is used to control user creation

### Important notes

- The custom user model must be defined **before running initial migrations**
- All future relations to users must use `settings.AUTH_USER_MODEL`
- The model is designed to match the frontend requirements (email-based login and fullname usage)
