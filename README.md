# AI MOOC Interview & Assessment System

A React and FastAPI application for technical assessments. Candidates choose a subject and difficulty, answer ten AI-generated or built-in multiple-choice questions, review their score, and download a PDF report after submitting, whether they pass or fail.

## Features

- Registration and login with hashed passwords and expiring bearer tokens.
- Ten subjects and three difficulty levels (Beginner, Intermediate, Advanced), with ten questions per assessment.
- AI-generated questions when the configured provider is available, plus a built-in offline question bank when it is not.
- Four options per question; answer keys remain on the backend until submission.
- Saved answers, server-side scoring, answer review, and performance feedback.
- Retakes create a new attempt and preserve earlier attempts in history.
- A score must be **greater than 80%** to pass. With ten questions, 9/10 (90%) is the minimum passing score; 8/10 (80%) requires a retake.
- Only passing assessments can be finally submitted. Final submission records a timestamp and locks that attempt on the backend.
- PDF reports are built from the stored assessment and answer records.

## Architecture

| Area | Stack | Entry points |
| --- | --- | --- |
| Frontend | React 18, React Router, Vite, Axios | `frontend/src/App.jsx`, `frontend/src/services/api.js` |
| Backend | FastAPI, Pydantic, SQLAlchemy | `backend/app/main.py`, `backend/app/routes/` |
| Database | SQLite for local development | `backend/app/database.py`, `backend/app/models/` |
| AI | OpenAI or Anthropic, selected in backend environment | `backend/app/services/ai_service.py` |
| PDF | ReportLab | `backend/app/services/pdf_service.py` |

The backend creates new tables at startup and adds the attempt fields to older SQLite databases without deleting existing assessment rows. The local database file is `backend/ai_mooc.db`.

## Requirements

- Python 3.10 or newer
- Node.js 20.19 or newer and npm 10 or newer
- An API key for fresh AI-generated questions (optional for local use)

## Setup

From the project root, install backend dependencies and create the backend environment file:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `backend/.env` and set `OPENAI_API_KEY`, or set `AI_PROVIDER=claude` and `CLAUDE_API_KEY`. The selected key stays on the backend. The frontend does not need an API key or a `.env` file; Vite proxies `/api` requests to the backend.

In a second terminal, install the frontend packages:

```powershell
cd frontend
npm install
```

The setup scripts `setup.bat` and `setup.sh` can also install both halves of the project.

## Run locally

Start the API in one terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Start the frontend in another terminal:

```powershell
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). API documentation is available at [http://localhost:8001/docs](http://localhost:8001/docs).

To create the optional local demo account, run this from `backend`:

```powershell
python seed.py
```

Demo login: `demo@example.com` / `demo1234`. Demo accounts are for local development only.

## Assessment rules

1. Creating an assessment validates the selected subject and one of three difficulty levels (Beginner, Intermediate, Advanced), requests questions from the configured AI provider, and saves a validated ten-question set as a new attempt. If the key is missing, rejected, or the provider is unavailable, it automatically uses the built-in question bank and labels the assessment accordingly.
2. The question endpoint returns only the question text and options. It never returns the correct answer or explanation before submission.
3. Answer changes are checked against questions in that user's attempt. The backend calculates the score; the client cannot submit a score.
4. An unanswered question counts as unanswered, not wrong. The percentage is `correct answers / 10 × 100`.
5. `percentage > 80` passes. `percentage <= 80` requires a retake. The final-submit endpoint rechecks this rule.
6. Retake creates another assessment ID in the same attempt group. A new assessment starts at attempt 1.
7. A finally submitted attempt cannot be edited, re-scored, re-submitted, or retaken. A PDF report is available after the first submission for both passing and failing results, and remains available after final submission. The candidate can begin another assessment.

## API overview

Protected endpoints require `Authorization: Bearer <access_token>`.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register` | Register and return an access token |
| POST | `/api/auth/login` | Sign in and return an access token |
| GET | `/api/auth/me` | Read the current profile |
| GET | `/api/subjects/` | List subjects |
| GET | `/api/subjects/difficulties` | List difficulty levels |
| GET | `/api/assessments/` | List the current user's attempts |
| GET | `/api/assessments/stats/dashboard` | Read dashboard statistics |
| POST | `/api/assessments/` | Create an attempt |
| GET | `/api/assessments/{id}/questions` | Read questions and saved answers, without the answer key |
| POST | `/api/assessments/{id}/answers` | Save one answer |
| POST | `/api/assessments/{id}/submit` | Evaluate and return the result |
| GET | `/api/assessments/{id}/result` | Read a stored completed result |
| POST | `/api/assessments/{id}/retake` | Create the next attempt in the group |
| POST | `/api/assessments/{id}/final-submit` | Finalize and lock a passing attempt |
| GET | `/api/assessments/{id}/pdf` | Download the stored report |

Unknown or another user's assessment IDs return `404`. Locked mutations return `403`. Invalid requests return validation errors without changing the assessment.

## Environment variables

`backend/.env.example` documents the supported variables. The configured development `.env` file is preserved by the setup scripts.

| Variable | Use |
| --- | --- |
| `DATABASE_URL` | Local SQLite connection string; defaults to `sqlite:///./ai_mooc.db` |
| `JWT_SECRET_KEY` | Signing key; set a unique value of at least 32 characters in production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Bearer-token lifetime; defaults to 30 minutes |
| `AI_PROVIDER` | `openai` or `claude` |
| `OPENAI_API_KEY` / `CLAUDE_API_KEY` | Secret for the selected provider |
| `OPENAI_MODEL` / `CLAUDE_MODEL` | Optional model identifiers |
| `AI_TIMEOUT_SECONDS` | Provider request timeout |
| `ENVIRONMENT` | Set to `production` for production validation |
| `DEBUG` | Must be false when `ENVIRONMENT=production` |
| `CORS_ORIGINS` | Comma-separated frontend origins |
| `ALLOWED_HOSTS` | Comma-separated API hostnames |

Question generation runs automatically when a candidate starts an assessment. With a working provider and valid key it uses AI-generated questions. If no usable key is configured or the provider cannot return a valid set, it automatically uses the built-in bank for the selected subject and difficulty, so local assessments continue to work. The assessment page identifies when this fallback was used. Set a valid provider key in `backend/.env` for fresh AI-generated questions; do not paste the key into the frontend or chat. Feedback generation is separate from scoring; if feedback is unavailable, the backend returns a deterministic learning summary.

## Quality checks

Run backend API tests from `backend`:

```powershell
python -m pytest -q
```

The tests use an isolated in-memory database and mock the AI provider; they do not read or modify `backend/ai_mooc.db` and do not require provider credentials.

Check the frontend from `frontend`:

```powershell
npm run lint
npm run build
```

## Security notes

- Passwords are bcrypt-hashed; registration limits passwords to the bcrypt input limit.
- Bearer tokens are sent in the `Authorization` header, not in URL query parameters.
- Assessment reads and mutations are scoped to the authenticated user.
- API keys are backend-only; frontend question responses exclude correct answers and explanations until evaluation.
- Authentication and AI-backed assessment creation have per-process request limits. Multi-worker deployments should also apply shared rate limits at the API gateway or reverse proxy.
- Production startup rejects the development JWT secret and `DEBUG=True`. Configure allowed hosts and CORS origins for the deployment.
