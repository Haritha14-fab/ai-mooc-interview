# Installation

The supported local setup and run instructions are maintained in [`README.md`](README.md).

## Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set `OPENAI_API_KEY`, or choose Claude with `AI_PROVIDER=claude` and `CLAUDE_API_KEY`, in `backend/.env`.

Run the API in one terminal and the frontend in another:

```powershell
# Terminal 1, from backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# Terminal 2, from frontend
npm install
npm run dev
```

Open http://localhost:3000. Visit http://localhost:8001/docs for API documentation.

## Tests and build

```powershell
# From backend
python -m pytest -q

# From frontend
npm run lint
npm run build
```

Tests use an in-memory SQLite database and mock AI responses. See [`README.md`](README.md) for API endpoints, configuration, data behavior, and the strict 80% pass rule.
