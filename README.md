# TaskTracker BackEnd (FastAPI)

REST API for the LearnGCP TaskTracker app.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/tasks` | List tasks (newest first) |
| POST | `/tasks` | Create task (JSON body) |
| POST | `/tasks/with-attachment` | Create task with optional file (`multipart/form-data`) |
| GET | `/tasks/stats` | Totals and completion rate |
| GET | `/tasks/{id}` | Get one task |
| PATCH | `/tasks/{id}` | Update title, description, or `completed` |
| DELETE | `/tasks/{id}` | Delete task |

## Local run (on your other machine)

```bash
python -m venv .venv
# Before executing this activation command, need to understand few things.
# Refer below section "SCRIPT CREATION/ACTIVATION STANDARDS"
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Start Postgres and set DATABASE_URL, or use docker-compose from the repo root (Module 1)
uvicorn app.main:app --reload --port 8080
```

API docs: http://localhost:8080/docs

## GCP hooks (later modules)

Set in `.env` when you wire Cloud Storage and Pub/Sub:

- `GCP_PROJECT_ID`
- `GCS_BUCKET`
- `PUBSUB_TOPIC`

Without these, attachments save under `ATTACHMENTS_DIR` and events are logged.

## Tests

```bash
pytest
```

## Docker

```bash
docker build -t tasktracker-backend .
docker run --rm -p 8080:8080 -e DATABASE_URL=postgresql://... tasktracker-backend
```

SCRIPT CREATION/ACTIVATION STANDARDS
------------------------------------
On Windows, python -m venv .venv puts activate scripts in .venv\Scripts, not .venv\bin\ folder.

If Powershell -
.\.venv\Scripts\Activate.ps1 (On Windows PowerShell, source is not a command.)

If CommandPrompt -
.\.venv\Scripts\activate.bat

If GitBash/WSL/Mac/Linux -
source .venv/Scripts/activate


Requirements Installation Behaviour:
------------------------------------
pip install -r requirements.txt command gave error on WSL window and not in powershell window. Why?


Same command, two different computers — from the shell’s point of view.

Short answer
pip install -r requirements.txt runs whatever pip is on your PATH in that window.

In PowerShell, after activating, pip was Windows pip inside your Windows .venv → it worked.
In WSL, after “activating”, pip was not a working Linux pip in a matching venv → Linux said pip command not found.

DB Setup:
---------
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost
postgres-# CREATE USER yusuf WITH PASSWORD '<<>>';
postgres-# CREATE DATABASE tasktracker OWNER yusuf;
postgres-# GRANT ALL PRIVILEGES ON DATABASE tasktracker TO yusuf;
postgres-# \q

& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 --> open psql as postgres
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U yusuf -h 127.0.0.1 -d --> login as tasktracker

Test Case:
---------
pytest --> execute this to run test cases