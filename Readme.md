# Student Management API

A simple RESTful API built with Flask for managing student records. This application provides CRUD (Create, Read, Update, Delete) operations for student data with SQLite database support.

## Features

- **GET /api/v1/students** - Retrieve all students
- **GET /api/v1/students/{id}** - Retrieve a specific student by ID
- **POST /api/v1/students** - Create a new student
- **PUT /api/v1/students/{id}** - Update an existing student
- **DELETE /api/v1/students/{id}** - Delete a student
- **GET /healthcheck** - API health status

## Tech Stack

- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Migrate** - Database migration support
- **SQLite** - Database (configurable via environment variables)
- **Python-dotenv** - Environment variable management

## Installation

### Prerequisites

- Python 3.7 or higher
- Make (optional, for using Makefile commands)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd student-management-api
```

2. Create a virtual environment and install dependencies:
```bash
make venv/bin/activate
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory(for developement):
```env
SQLITE_DB=sqlite:///students.db
```

## Usage

### Development Mode

```bash
make serve-dev
```

This will:
- Run database migrations
- Start the Flask development server on `http://localhost:5000`

### Production Mode

```bash
make serve-prod
```

This will:
- Run database migrations
- Start the application using Gunicorn

## Docker
If you have Docker.You can use the below commands:
``` bash
make build
make serve-docker
```

## Database Schema

### Student Model
- **id** (Integer, Primary Key) - Auto-generated student ID
- **first_name** (String, Required) - Student's first name
- **last_name** (String, Required) - Student's last name
- **age** (Integer, Required) - Student's age
- **email** (String, Required, Unique) - Student's email address

## Development

### Database Migrations

To create a new migration:
```bash
make migrate
```

### Running Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### Clean Up

To remove virtual environment and cache files:
```bash
make clean
```

## Configuration

The application uses environment variables for configuration:

- **SQLITE_DB** - Database connection string (Example: sqlite:///students.db)

## Project Structure

```
student-management-api/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── Makefile           # Build and deployment commands
├── .env               # Environment variables
├── migrations/        # Database migration files
├── tests/            # Unit tests
└── README.md         # This file
```

