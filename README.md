# Day 19 — Deploying FastAPI to Production

Day 19 of #60DaysOfPython — Took the Day 18 FastAPI + pytest project and deployed it live: swapped SQLite for a managed Postgres database, picked a hosting platform, and got every endpoint working against a real production database.

**Live API:** [day19-deployment-production.up.railway.app](https://day19-deployment-production.up.railway.app/docs)

## What Changed from Day 18

- Swapped local SQLite for a managed **Supabase Postgres** database
- Updated `database.py` to read the connection string from an environment variable (`DATABASE_URL`) instead of hardcoding SQLite
- Removed all secrets from source control — `SECRET_KEY` and `DATABASE_URL` now live only in the hosting platform's environment variables
- Fixed the Uvicorn start command to bind to `0.0.0.0` and read the platform's dynamic `$PORT`, instead of the local-dev default

## Deployment Journey

Started with **Render** as the first choice (generous permanent free tier, no time limit). Hit a wall trying to provision a database — Render requires card verification (a refundable $1 authorization) before creating any database, even on the free tier. Decided not to add a card for a learning project at this stage.

Pivoted to a two-platform setup instead:

- **Database → Supabase** — free managed Postgres, no card required, generated in the Southeast Asia (Singapore) region for low latency
- **App hosting → Railway** — connected the GitHub repo, deployed straight from `main`

This split (one platform for the app, another for the database) ended up being a useful pattern in itself: it decouples hosting decisions from data persistence decisions.

## Verifying the Deploy

Tested the full request lifecycle against the live database, not just that the server started:

- `/docs` loads the Swagger UI with all endpoints listed
- `/register` creates a user — confirmed the row appears in Supabase's Table Editor
- `/login` returns a valid JWT
- Protected routes (`/me`, `/dashboard`) correctly accept the token and enforce role checks

## Tech Stack

- **FastAPI** — API framework
- **Supabase (Postgres)** — managed production database
- **SQLAlchemy** — ORM, now pointed at Postgres instead of SQLite
- **Pydantic v2** — request/response validation
- **python-jose** — JWT generation and verification
- **passlib + bcrypt** — password hashing
- **Railway** — application hosting / deployment
- **pytest + httpx** — test runner and HTTP client (carried over from Day 18)

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Supabase Postgres connection string (pooler) |
| `SECRET_KEY` | JWT signing secret |

Set these in Railway's **Variables** tab — never committed to the repo.

## Setup & Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Run Tests

```bash
pytest -v
```

## Lessons Learned

- A "free tier" can still gate specific features (like databases) behind card verification — worth checking before committing to a platform
- Splitting app hosting and database hosting across two free-tier-friendly platforms is a practical workaround for early-stage projects
- Connection pooling matters: Supabase's pooler connection (port 6543) is the safer choice for apps on PaaS platforms versus the direct connection (port 5432)

## Part of

[#60DaysOfPython](https://github.com/studyhaxer) — rebuilding to professional software development, one project a day.
