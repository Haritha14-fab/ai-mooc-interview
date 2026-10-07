# Quick reference

Use `README.md` for complete setup and architecture documentation.

## Start the project (Windows PowerShell)

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Open http://localhost:3000. The API docs are at http://localhost:8001/docs.

## Checks

```powershell
# From backend
python -m pytest -q

# From frontend
npm run lint
npm run build
```

Backend tests use a temporary in-memory database and a mocked AI provider.

## Assessment rules

- Ten questions, four options per question.
- Answers are saved through the backend; correct answers stay private until evaluation.
- `percentage > 80` passes. `percentage <= 80` requires a retake.
- 9/10 = 90% = pass. 8/10 = 80% = retake required.
- Retakes get a new assessment ID and increment the attempt number.
- Only a passed attempt can be finally submitted. Final submission locks that attempt on the backend.
- Each user's history and reports are scoped to their account.

## Configuration

Edit `backend/.env`: set `AI_PROVIDER` to `openai` or `claude`, then add the matching API key. Never put AI keys in the frontend. See `backend/.env.example` for all settings.

## Main routes

| Purpose | Endpoint |
| --- | --- |
| Register / login / profile | `/api/auth/register`, `/api/auth/login`, `/api/auth/me` |
| Subjects and levels | `/api/subjects/`, `/api/subjects/difficulties` |
| Create/list attempts | `POST /api/assessments/`, `GET /api/assessments/` |
| Questions and answers | `GET /api/assessments/{id}/questions`, `POST /api/assessments/{id}/answers` |
| Score and report | `POST /api/assessments/{id}/submit`, `GET /api/assessments/{id}/result`, `GET /api/assessments/{id}/pdf` |
| Retake and lock | `POST /api/assessments/{id}/retake`, `POST /api/assessments/{id}/final-submit` |

Protected requests use `Authorization: Bearer <access_token>`.
