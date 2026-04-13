# KanMind Backend

Backend for the KanMind application built with Django and Django REST Framework.

This project was developed as part of the Developer Akademie backend course.

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
    - [Important Note](#important-note)
  - [API Routing Overview](#api-routing-overview)
    - [Authentication](#authentication)
    - [Boards](#boards)
    - [Tasks](#tasks)
  - [Tech Stack](#tech-stack)
  - [Project Structure](#project-structure)
  - [Project Status](#project-status)
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
  - [Known Limitations](#known-limitations)

## Frontend

The corresponding frontend for this project is provided by the Developer Akademie and can be found here:

[KanMind Frontend Repository](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)

The frontend serves as a reference implementation and can be used to test and interact with the API endpoints of this backend.

### Important Note

The frontend is configured to communicate with a local backend:

`API_BASE_URL = http://127.0.0.1:8000/api/`

This means:

- The backend must be running locally for the frontend to function correctly
- The deployed frontend (e.g. on a file server) is for UI demonstration only
- Full functionality requires starting the Django backend locally

## API Routing Overview

The API routing is fully structured according to the provided specifications and aligned with the frontend configuration.

The following API endpoints are available:

### Authentication

- `/api/registration/`
- `/api/login/`
- `/api/email-check/`

### Boards

- `/api/boards/`
- `/api/boards/{board_id}/`

### Tasks

- `/api/tasks/`
- `/api/tasks/assigned-to-me/`
- `/api/tasks/reviewing/`
- `/api/tasks/{task_id}/`
- `/api/tasks/{task_id}/comments/`
- `/api/tasks/{task_id}/comments/{comment_id}/`

All routes are organized in a modular structure using app-specific API modules and centralized routing via `core/urls.py`.

## Tech Stack

- Django
- Django REST Framework

## Project Structure

The project follows a modular and scalable architecture based on Django apps.

It includes:

- a central `core` project configuration
- dedicated apps for authentication, boards, and tasks
- structured API layers within each app, including:
  - serializers
  - views
  - permissions
  - URL configuration

This separation ensures clear responsibilities, maintainability, and extensibility of the codebase.

## Project Status

The KanMind backend has been fully implemented and tested.

The project includes:

- a complete authentication system using token-based authentication
- fully implemented API endpoints for boards, tasks, and comments
- structured and modular API architecture across all apps
- object-level permission handling using Django REST Framework
- integration with the provided frontend for end-to-end testing

All endpoints have been validated using both frontend interaction and API testing tools (e.g. Postman), including correct handling of HTTP status codes and edge cases.

The project is considered feature-complete within the scope of the assignment.

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

- Board access (GET, PATCH) is restricted to board owner and members
- Board deletion is restricted to the board owner

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

Permissions are implemented using Django REST Framework permission classes based on `BasePermission`.

Object-level permissions are enforced using:

- `get_permissions()` for dynamic permission handling per request method
- `check_object_permissions()` for object-specific access control

Custom permission classes include:

- `IsBoardOwnerOrMember`
- `IsBoardOwner`
- `IsTaskCreatorOrBoardOwner`
- `IsCommentAuthor`

## Task Ownership and Responsibilities

Each task defines clear responsibilities:

- **Assignee** → responsible for executing the task
- **Reviewer** → responsible for validating the result
- **Members** → optional collaborators involved in the task
- **Creator** → the user who originally created the task (used for permission checks such as deletion)

This structure enables clear task ownership, review workflows, and team collaboration.

## Known Limitations

- Task deletion is not exposed in the provided frontend UI
- Some backend features are only testable via API tools (e.g. Postman)
- These limitations are related to the provided frontend implementation and do not affect the backend functionality.
