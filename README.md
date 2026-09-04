# TeamFlow

A backend project management REST API built with **Django REST Framework**, designed with real-world backend engineering practices including role-based access control, Redis caching, asynchronous processing with Celery, MySQL, API throttling, automated testing, OpenAPI documentation, and Docker.

---

## Overview

**TeamFlow** is a project management backend that enables organizations to manage projects, team members, tasks, and task comments through a RESTful API.

The project goes beyond basic CRUD by implementing backend concepts such as:

* Role-based authorization
* Custom user authentication
* Redis caching and cache invalidation
* Asynchronous task processing
* Transaction-safe background jobs
* Filtering and pagination
* API throttling
* Automated testing
* Environment-based configuration
* Containerized infrastructure

---

## Key Features

### Authentication & Authorization

* Custom User model
* JWT authentication
* User registration and authentication
* Role-based access control
* Organization-level permissions
* Project-level permissions

### Organizations

Organizations provide the top-level structure for managing users and projects.

Supported roles:

* System Administrator
* Organization Administrator
* Project Manager
* Team Member

### Projects

* Project creation and management
* Project manager assignment
* Project member management
* Role-based project access

### Tasks

* Task creation and management
* Task assignment
* Task status and priority
* Task filtering
* Pagination
* Permission-based task operations

### Comments

* Task comments
* Comment retrieval
* Comment updates and deletion
* Permission-based comment operations

---

## Caching

TeamFlow uses **Redis** with `django-redis` for application-level caching.

The API follows a **cache-aside** strategy:

```text
Request
   │
   ▼
Redis Cache
   │
   ├── Cache HIT ──────► Return response
   │
   └── Cache MISS
          │
          ▼
       MySQL
          │
          ▼
    Serialize data
          │
          ▼
      Store in Redis
          │
          ▼
      Return response
```

Caching includes:

* User-specific cache keys
* Pagination-aware cache keys
* Filter-aware cache keys
* TTL-based expiration
* Explicit cache invalidation

Redis databases are logically separated:

```text
Redis DB 0 → Celery broker
Redis DB 1 → Django application cache
```

---

## Asynchronous Processing

TeamFlow uses **Celery** with Redis as the message broker for background processing.

The main asynchronous workflow is task-assignment email notification.

```text
Django API
    │
    ▼
Task assigned / reassigned
    │
    ▼
transaction.on_commit()
    │
    ▼
Celery task
    │
    ▼
Redis broker
    │
    ▼
Celery worker
    │
    ▼
Email notification
```

Notifications are triggered only when a task is newly assigned or reassigned, avoiding unnecessary emails for unrelated task updates.

`transaction.on_commit()` ensures the background task is triggered only after the database transaction has successfully committed.

---

## Filtering, Pagination & Throttling

### Filtering

Task APIs support filtering by:

* Status
* Priority

Filtering is implemented using **django-filter** and integrated with the application's custom caching strategy.

### Pagination

TeamFlow uses global DRF pagination with configurable page sizes.

Pagination parameters are included in cache keys to ensure different pages are cached independently.

### Throttling

DRF throttling is enabled to help protect API endpoints from excessive requests.

---

## API Documentation

The API is documented using **OpenAPI** and **drf-spectacular**.

### Swagger UI

```text
/api/docs/
```

### ReDoc

```text
/api/redoc/
```

### OpenAPI Schema

```text
/api/schema/
```

Swagger provides an interactive interface for exploring the complete API, including endpoints, request schemas, responses, authentication requirements, and available operations.

---

## Testing

TeamFlow includes automated tests covering the application's major modules and backend behavior.

Testing covers:

* Authentication and user management
* Organizations and permissions
* Projects and project members
* Tasks and task permissions
* Comments
* Filtering and pagination
* Redis caching
* Cache invalidation
* Task assignment behavior
* API validation and responses

The project uses Django's testing framework together with Django REST Framework's API testing utilities.

---

## Architecture

```text
                         Client
                           │
                           ▼
                  Django REST API
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          MySQL          Redis         Celery
         Database        Cache         Worker
                           │             │
                           │             ▼
                           │       Email Service
                           │
                           └── Message Broker
```

### Containerized Architecture

The application infrastructure is managed using **Docker Compose**.

```text
                    Docker Compose
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
     Django           Celery           MySQL
      API             Worker          Database
        │                │
        └────────┬───────┘
                 ▼
               Redis
```

Django and Celery run from the same application image with different runtime commands.

---

## Docker

TeamFlow uses Docker and Docker Compose to containerize the application and its supporting services.

The environment consists of:

* Django API
* Celery worker
* MySQL database
* Redis

The application uses a **multi-stage Docker build**.

Build dependencies required for compiling Python packages are kept in the builder stage and are not included in the final runtime image.

This reduced the application image size from approximately **826 MB to approximately 380 MB**.

---

## Environment Configuration

Application configuration is managed through environment variables using **python-decouple**.

Configuration includes:

```text
SECRET_KEY
DEBUG
Database credentials
Redis configuration
Celery configuration
Email credentials
```

Sensitive environment files are excluded from version control.

The application separates configuration from source code, allowing environment-specific settings without modifying the application itself.

---

## Project Structure

```text
TeamFlow/
│
├── accounts/          # Users and authentication
├── organizations/     # Organizations and roles
├── projects/          # Projects and project members
├── tasks/             # Tasks, filtering and background tasks
├── comment/           # Task comments
├── common/            # Shared components
│
├── config/            # Django project configuration
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
├── manage.py
└── README.md
```

---

## Technology Stack

| Category          | Technology                  |
| ----------------- | --------------------------- |
| Language          | Python                      |
| Framework         | Django                      |
| API               | Django REST Framework       |
| Authentication    | JWT                         |
| Database          | MySQL                       |
| Cache             | Redis                       |
| Background Tasks  | Celery                      |
| Filtering         | django-filter               |
| API Documentation | drf-spectacular / OpenAPI   |
| Testing           | Django Test Framework / DRF |
| Configuration     | python-decouple             |
| Containerization  | Docker                      |
| Orchestration     | Docker Compose              |
| Version Control   | Git / GitHub                |

---

## Future Improvements

* CI/CD with GitHub Actions
* Production deployment
* Production WSGI server configuration
* Production security hardening
* Production infrastructure configuration
