# Phase 2 hosted database setup

## Supabase values

Create a hosted Supabase project and obtain the PostgreSQL connection string from its Connect panel. Prefer the session pooler URL if the direct endpoint is not reachable over IPv4.

Place values in the repository-root `.env` file:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require
DATABASE_MIGRATION_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require
```

Percent-encode reserved characters in the password. Never add `.env` to Git.

## Apply and verify

From `backend`:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m app.db.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000/api/v1/database/status`. A successful response identifies Supabase, reports the PostGIS version and schema revision, and counts the ten controlled lookup records.
