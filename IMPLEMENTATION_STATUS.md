# Implementation status

This document is a short feature inventory. `README.md` is the source of truth for setup and operation.

## Included

- React/Vite client and FastAPI/SQLAlchemy API.
- Registration, login, bearer-token authentication, and per-user assessment access.
- Ten supported subjects and four difficulty levels.
- Validated ten-question generation through OpenAI or Anthropic; failures do not persist partial attempts.
- Backend-owned answer evaluation, including the strict `percentage > 80` pass rule.
- Saved and editable answers before final submission.
- New IDs and incrementing attempt numbers for retakes, with earlier attempts retained in history.
- Backend enforcement for passing-only final submission and permanent attempt locking.
- Completed assessment reports and backend-generated PDF downloads.
- Database migration for attempt metadata on existing assessment tables.
- API tests with an isolated in-memory database and mocked AI provider.

## Local verification commands

```powershell
# Backend
python -m pytest -q

# Frontend
npm run lint
npm run build
```

The AI provider must be configured in `backend/.env` to generate real assessments. The tests do not require provider credentials. See `README.md` for remaining configuration details.
