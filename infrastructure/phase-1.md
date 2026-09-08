# Phase 1 operation

## Native development

Backend terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`.

## Docker development

```powershell
docker compose up --build
```

Hosted databases are not embedded in these containers. They enter the project in Phase 2.

## Production configuration

The Render blueprint deploys the frontend as static assets and FastAPI as a stateless container. Set `VITE_API_BASE_URL` to the public API URL and `APP_CORS_ORIGINS` to the public frontend origin.
