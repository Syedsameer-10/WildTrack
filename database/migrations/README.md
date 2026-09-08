# Database migrations

Executable Alembic revisions live in `backend/migrations` so they are packaged with the deployable API container. Applied revisions are never edited retroactively; corrections use a new migration.

From `backend`, run:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```
