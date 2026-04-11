# KanMind Backend

Backend for the KanMind application built with Django and Django REST Framework.

## Setup / Quick-Start

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

## Table of Contents

- [KanMind Backend](#kanmind-backend)
  - [Setup / Quick-Start](#setup--quick-start)
  - [Table of Contents](#table-of-contents)
  - [Frontend](#frontend)
  - [API Routing Overview](#api-routing-overview)
  - [Tech Stack](#tech-stack)
  - [Current Project Structure](#current-project-structure)
  - [Current Project Status](#current-project-status)
  - [Environment Setup](#environment-setup)
    - [Setup instructions](#setup-instructions)
  - [Custom User Model](#custom-user-model)
    - [Key characteristics](#key-characteristics)
    - [Implementation details](#implementation-details)
    - [Important notes](#important-notes)
  - [Data Model Overview](#data-model-overview)
    - [User](#user)
    - [Board](#board)
    - [Task](#task)
    - [Comment](#comment)
  - [Relationships](#relationships)
    - [from Board](#from-board)
    - [from Task](#from-task)
    - [from Comment](#from-comment)
  - [Permissions](#permissions)
  - [Task Ownership and Responsibilities](#task-ownership-and-responsibilities)

## Frontend

The corresponding frontend for this project is provided by the Developer Akademie and can be found here:

[KanMind Frontend Repository](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)

The frontend serves as a reference implementation and can be used to test and interact with the API endpoints of this backend.

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
- dedicated API folders inside each app for serializers, views, permissions and URL configuration

## Current Project Status

The backend base setup has been further extended with a modular API routing structure.

Current progress includes:

- integration of token authentication using Django REST Framework
- CORS configuration for local frontend-backend communication
- centralized root URL configuration in `core/urls.py`
- initial API endpoint structure based on the provided documentation
- extraction of permission logic into dedicated permissions modules per app

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

## Data Model Overview

### User

Custom user model used for authentication.

- `email`
- `fullname`

---

### Board

Represents a workspace that contains tasks and members.

- `title`
- `owner` (User)
- `members` (User)

- Task creation and updates are restricted to board owner and members
- Task deletion is restricted to the creator or the board owner

---

### Task

Represents a work item within a board.

- `title`
- `description`
- `status` (`to-do`, `in-progress`, `review`, `done`)
- `priority` (`low`, `medium`, `high`)
- `assignee` (User)
- `reviewer` (User)
- `members` (User)
- `created_by` (User)
- `due_date`

- Task creation and updates are restricted to board owner and members
- Task deletion is restricted to the creator or the board owner

---

### Comment

Represents user-generated activity on a task.

- `content`
- `author` (User)
- `task` (Task)
- `created_at`

- Only the author of a comment is allowed to delete it

---

## Relationships

### from Board

- `owner` → User (**1:n**)
- `members` ↔ User (**m:n**)

### from Task

- `board` → Board (**n:1**)
- `assignee` → User (**n:1**)
- `reviewer` → User (**n:1**)
- `members` ↔ User (**m:n**)
- `created_by` → User (**n:1**)

### from Comment

- `task` → Task (**n:1**)
- `author` → User (**n:1**)

---

## Permissions

Permission logic is centralized in dedicated `permissions.py` modules within each app.

This ensures:

- clear separation of concerns
- reusable permission checks
- cleaner view implementations

## Task Ownership and Responsibilities

Each task defines clear responsibilities:

- **Assignee** → responsible for executing the task
- **Reviewer** → responsible for validating the result
- **Members** → optional collaborators involved in the task
- **Creator** → the user who originally created the task (used for permission checks such as deletion)

This structure enables clear task ownership, review workflows, and team collaboration.
