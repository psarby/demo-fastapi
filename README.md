Demo FastAPI
============

Small FastAPI project with PostgreSQL, JWT auth, server-rendered pages, and
Alembic migrations.

Requirements
------------

- Python 3.14
- Docker Desktop
- Git

Local Setup
-----------

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create local environment file:

```bash
cp .env.example .env
```

Start PostgreSQL:

```bash
docker compose up -d
```

Run migrations:

```bash
python -m alembic upgrade head
```

Start the app:

```bash
uvicorn app.main:app --reload
```

If port 8000 is busy, use another port:

```bash
uvicorn app.main:app --reload --port 8010
```

Open:

- App: http://127.0.0.1:8000
- Login: http://127.0.0.1:8000/login
- Dashboard: http://127.0.0.1:8000/dashboard
- Swagger docs: http://127.0.0.1:8000/docs

Useful Commands
---------------

Check Docker config:

```bash
docker compose config
```

Check current migration:

```bash
python -m alembic current
```

Create a new migration after model changes:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
python -m alembic upgrade head
```

Stop PostgreSQL:

```bash
docker compose down
```

Environment
-----------

Local secrets live in `.env`. This file is ignored by Git. Use `.env.example`
as the template for new machines and deployments.

Required variables:

```env
DATABASE_URL=postgresql://demo_user:demo_pass@localhost:5432/demo_db
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Git Workflow
------------

```bash
git status
git add .
git commit -m "Short description of the completed step"
git push origin main
```
