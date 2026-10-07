# AI MOOC Interview & Assessment System

The project provides technical interview practice with AI-generated MCQ assessments. Candidates choose a subject and difficulty, complete ten questions, review the server-calculated result, and save a PDF report.

## Candidate flow

1. Register or sign in.
2. Choose one of ten subjects and one of four difficulty levels.
3. Answer and navigate the ten questions; answer choices are saved by the API.
4. Submit for scoring. Correct answers and explanations are shown only after evaluation.
5. Modify answers or create a new retake attempt before finalizing.
6. Finalize a passing result to lock that attempt. Start a separate assessment for another subject or test.

The pass condition is strictly greater than 80%. A result of 8/10 (80%) requires a retake; 9/10 (90%) passes.

## Technology

- Frontend: React 18, React Router, Vite, Axios
- Backend: FastAPI, Pydantic, SQLAlchemy
- Local database: SQLite
- Question and feedback providers: OpenAI or Anthropic
- Reports: ReportLab PDF

## Start here

Follow [`README.md`](README.md) for environment configuration, install and run commands, API details, security behavior, and quality checks. `INSTALL.md` and `QUICK_REFERENCE.md` provide shorter command references.
