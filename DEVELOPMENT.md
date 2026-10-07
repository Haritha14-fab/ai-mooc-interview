# Development guide

Start with [`README.md`](README.md) for dependencies, environment setup, and run commands.

## Project layout

```text
backend/
  app/auth/          bearer authentication and password/JWT helpers
  app/models/        SQLAlchemy users, assessments, questions, and answers
  app/routes/        auth, subject, and assessment APIs
  app/schemas/       Pydantic request and response contracts
  app/services/      AI generation, scoring, and PDF report generation
  app/utils/         supported subjects, levels, status, and scoring constants
  tests/             isolated API and business-rule tests
frontend/
  src/components/    shared navigation and protected routes
  src/context/       authentication state
  src/pages/         dashboard, assessment, history, and report screens
  src/services/      Axios API client and bearer-token handling
  src/styles/        page and responsive styles
```

## Assessment lifecycle

```text
in_progress → submitted → final_submitted
       │           │
       │           └─ answer changes recalculate the stored result
       └─ retake is offered after evaluation and creates a new attempt
```

`final_submitted` is an irreversible backend state for that attempt. The API checks ownership and lock status for every assessment operation. A retake links to its attempt group and increments the attempt number; a separately created assessment starts at 1.

Scoring is deterministic and belongs to `ScoringService`. The pass check is strictly `percentage > PASS_THRESHOLD`; 80% does not pass. AI feedback is generated after the score is stored and is never used to determine the result.

## Authentication and API usage

Register and login return a bearer token. Protected endpoints read it from `Authorization: Bearer <token>`. Do not put tokens or provider keys in query strings. The frontend sends the bearer token through the shared Axios service. Authenticated assessment queries always filter by both assessment ID and the current user's ID.

## AI provider behavior

`AIService` selects OpenAI or Anthropic from `AI_PROVIDER`. It requires the matching server-side API key, asks for ten MCQs, validates the response, and retries once if the structure or content is invalid. If generation still fails, it returns an API error and the assessment is not saved. Feedback errors fall back to a deterministic summary.

When adding a provider, keep the interface in `AIService` and preserve validation before persistence. Never return `correct_answer` or `explanation` from the in-progress question endpoint.

## Database behavior

`create_tables()` creates missing tables and adds `attempt_number` and `attempt_group_id` to earlier assessment tables. Existing records are migrated as attempt 1 in their own group. Database tests use a separate in-memory engine; they must not target `backend/ai_mooc.db`.

## Add a subject or difficulty

Add the value to `backend/app/utils/constants.py`. The API validates new assessment requests against those lists. The frontend renders returned values; subject icons are optional and have a fallback. Add representative provider-generated content to the API tests if a new subject-specific rule is introduced.

## Checks

From `backend`:

```powershell
python -m pytest -q
```

From `frontend`:

```powershell
npm run lint
npm run build
```

The API tests mock the AI provider and verify scoring boundaries, answer privacy, answer updates, attempt history, ownership, final locking, PDF generation, and provider-failure behavior.
