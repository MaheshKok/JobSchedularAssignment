# Job Scheduler

A Django-based web application that allows users to submit jobs to be processed by a background system. The scheduler handles priority-based execution and provides a dashboard for monitoring job statuses in real-time.

## Features

- User authentication and registration
- Job submission via web form or API
- Custom job scheduling algorithm with priority and deadline-based scheduling
- Real-time dashboard for monitoring job statuses
- REST API for job management
- WebSocket support for real-time updates

## Technical Stack

- Backend: Django + Django REST Framework
- Database: PostgreSQL
- Frontend: HTML/CSS/JavaScript + Bootstrap
- Real-time: Django Channels + WebSockets
- Background processing: Custom scheduler with thread pool

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Channels and WebSockets)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with:

   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database settings
   DB_NAME=job_scheduler
   DB_USER=postgres
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432

   # Redis settings
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

5. Create the database:
   ```
   createdb job_scheduler  # If using PostgreSQL CLI
   ```
6. Apply migrations:
   ```
   cd job_scheduler
   python manage.py migrate
   ```
7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

## Running the Application

1. Start the development server:
   ```
   python manage.py runserver
   ```
2. Start the job scheduler:
   ```
   python manage.py start_scheduler
   ```
3. Visit http://127.0.0.1:8000 in your browser

## API Endpoints

- `GET /jobs/api/jobs/` - List all jobs
- `POST /jobs/api/jobs/` - Create a new job
- `GET /jobs/api/jobs/{id}/` - Get a specific job
- `PUT /jobs/api/jobs/{id}/` - Update a job
- `DELETE /jobs/api/jobs/{id}/` - Delete a job
- `GET /jobs/api/jobs/stats/` - Get job statistics
- `GET /jobs/api/jobs/{id}/executions/` - Get job execution history

## Scheduling Algorithm

The scheduler uses a hybrid approach:

1. Priority Queue - Jobs are first sorted by priority (High > Medium > Low)
2. Earliest Deadline First (EDF) - Within each priority level, jobs are sorted by deadline

The system limits concurrent job execution to 3 jobs at a time.

## License

MIT
