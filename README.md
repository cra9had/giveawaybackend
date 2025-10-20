# GiveawayBackend — Backend API (Django / DRF)

## Description
GiveawayBackend is the backend of a web application for organizing and managing giveaways.  
Built with Django + Django REST Framework.  
It provides APIs for creating, managing, and participating in giveaways.

## Features

- 🏆 **Giveaway management**: create, edit, delete giveaways  
- 🎟 **User participation**: enter giveaways, check eligibility  
- 👥 **Authentication / Authorization**: registration, login, JWT / tokens  
- 📄 **API for admins and users**  
- 📤 **Notifications / background tasks** 
- 📸 **Media / files** (for storing prize images, banners, etc.)  

## Technology Stack

- Python  
- Django  
- Django REST Framework  
- Database: PostgreSQL / SQLite (for local development)  
- Celery + Redis (for background tasks, optional)

## Installation & Local Setup

1. Clone the repository  
   ```bash
   git clone https://github.com/cra9had/giveawaybackend.git
   cd giveawaybackend
   ```

2. Create and activate a virtual environment  
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` → `.env` and fill in required variables (DB, secret key, tokens, etc.)

5. Run migrations and create a superuser  
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Run the development server  
   ```bash
   python manage.py runserver
   # default: http://127.0.0.1:8000/
   ```

7. Run background tasks with Celery  
   ```bash
   celery -A giveawaybot worker -l info
   celery -A giveawaybot beat -l info
   ```

## Workflow

1. Admin creates a giveaway (prize, conditions, duration)  
2. Users request a list of active giveaways  
3. Users enter giveaways if eligible  
4. When the giveaway ends, a winner is selected  
5. Results are published / notifications sent

## Deployment (production)

1. Set `DEBUG=False`, configure `ALLOWED_HOSTS`  
2. Apply migrations & collect static files  
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
3. Run via Gunicorn/Uvicorn + Nginx  
4. Configure persistent media storage (S3, MinIO, or local)  
5. Configure background services (Celery, Redis)  
6. Enable HTTPS, logging, and monitoring  


