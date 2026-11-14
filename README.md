# HireTrack – Backend

HireTrack is a job application management system backend built with Django and Django REST Framework. It provides REST APIs for managing job applications, attachments, follow-ups, notifications, and user authentication.

## Technology Stack

- Python
- Django 6.1.3
- Django REST Framework 3.18.3
- Django REST Framework SimpleJWT
- SQLite (local development)
- PostgreSQL (production database)
- django-cors-headers
- python-dotenv
- Gunicorn
- WhiteNoise
- django-storages
- Cloudflare R2 (optional object storage)
- boto3

## Main Features

- JWT-based authentication
- Job application management
- User-specific application access
- Resume and cover letter file handling
- Additional attachment management
- Follow-up tracking
- Notification management
- Secure, authenticated file downloads
- REST API endpoints

## Requirements

- Python
- pip
- A virtual environment
- Node.js and npm for running the separate frontend

## Installation

Open PowerShell in the backend project directory.

Create a virtual environment if one does not already exist:

    python -m venv .venv

Activate the virtual environment:

    .\.venv\Scripts\Activate.ps1

Install dependencies:

    pip install -r requirements.txt

## Environment Configuration

Create a `.env` file from the example template if it does not already exist:

    Copy-Item .env.example .env

Configure the required local development variables:

    SECRET_KEY=your-own-secret-key
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174

The `.env.example` file documents optional production database, storage, and email settings.

Never commit or share the real `.env` file or secret credentials.

## Database Setup

Apply database migrations:

    python manage.py migrate

Create an administrator account when needed:

    python manage.py createsuperuser

Local development uses SQLite and stores the database in `db.sqlite3`.

Production can use PostgreSQL through the `DATABASE_URL` environment variable.

## Run Development Server

    python manage.py runserver

The local backend server runs at:

    http://127.0.0.1:8000/

Django Admin:

    http://127.0.0.1:8000/admin/

## API Endpoints

### Authentication

- POST `/api/token/`
- POST `/api/token/refresh/`

### Application Management

- `/api/applications/`

### Attachment Management

- `/api/attachments/`

### Follow-up Management

- `/api/followups/`

### Notification Management

- `/api/notifications/`

Protected API endpoints use JWT authentication.

## Media Files

Local development uses Django FileSystemStorage. Uploaded files are stored under:

    media/

Media URL:

    /media/

During local development, Django serves media files when DEBUG is enabled.

For production, configure persistent object storage. The backend supports optional Cloudflare R2 integration through django-storages and the AWS-compatible environment variables documented in `.env.example`.

File downloads are handled through authenticated API endpoints with user ownership checks.

## Static Files

WhiteNoise is configured to serve collected static files in production.

Collect static files before deployment:

    python manage.py collectstatic --noinput

## Testing and Validation

Run Django system checks:

    python manage.py check

Run the tracker application tests:

    python manage.py test tracker

Check installed dependency consistency:

    python -m pip check

## Frontend Integration

The React frontend communicates with this backend through the REST API.

Default local API base URL:

    http://127.0.0.1:8000/api

Make sure the frontend origin is included in `CORS_ALLOWED_ORIGINS`.

## Production Deployment

Before deploying:

- Set `DEBUG=False`.
- Use a strong, private `SECRET_KEY`.
- Configure production `ALLOWED_HOSTS`.
- Configure `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` with the actual HTTPS frontend origin.
- Set `DATABASE_URL` to the production PostgreSQL connection URL.
- Configure persistent media storage, such as Cloudflare R2, using the required environment variables.
- Configure SMTP credentials if production email delivery is required.
- Ensure HTTPS is enabled at the hosting platform or reverse proxy.
- Run database migrations.
- Run `python manage.py collectstatic --noinput`.

Example production application server command:

    gunicorn config.wsgi:application

Run deployment checks with:

    python manage.py check --deploy

Do not enable HSTS until the production HTTPS domain and deployment are confirmed.

Never expose secret credentials or user-uploaded private files in source control.

## Project Structure

    hiretrack-backend/
    ├── config/
    ├── tracker/
    ├── media/
    ├── .env.example
    ├── manage.py
    ├── requirements.txt
    └── README.md
