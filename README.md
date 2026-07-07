# Workstation Advisor

Workstation Advisor is a full-stack web app that recommends workstation configurations based on workload needs.  
It supports two recommendation flows:

- **Natural language**: describe your work and get matched recommendations
- **Guided stepper**: choose archetype → industry → vertical → workload → scale

Users can also register, sign in, and save workload profiles.

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Backend**: Flask, Flask-Login, Flask-CORS, Flask-Limiter
- **Database**: PostgreSQL
- **LLM**: Anthropic API (used for natural-language workload matching/explanations)

## Repository Structure

```text
.
├── backend/   # Flask API, migrations, seed data, recommendation logic
└── frontend/  # React app
```

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- PostgreSQL
- Anthropic API key

## Local Setup

### 1) Backend

```bash
cd /home/runner/work/workstation-advisor/workstation-advisor/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .flaskenv.example .flaskenv
```

Update `backend/.flaskenv`:

- `DATABASE_URL` (PostgreSQL connection string)
- `SECRET_KEY` (secure random value)
- `ANTHROPIC_API_KEY` (required by the app at startup)

Run migrations and seed data:

```bash
alembic upgrade head
python seed.py
```

Start the API:

```bash
flask --app app.py run --port 5001
```

### 2) Frontend

```bash
cd /home/runner/work/workstation-advisor/workstation-advisor/frontend
npm install
cp .env.local.example .env.local
```

Set `VITE_API_URL` in `frontend/.env.local` (default: `http://localhost:5001`), then run:

```bash
npm run dev
```

Open the app at `http://localhost:5173`.

## Useful Commands

Frontend:

- `npm run dev` — start dev server
- `npm run build` — production build
- `npm run lint` — lint frontend code

Backend:

- `flask --app app.py run --port 5001` — run API
- `alembic upgrade head` — apply migrations
- `python seed.py` — seed taxonomy/products data

## API Overview

Key routes under `/api`:

- `GET /api/taxonomy` — workload taxonomy for guided flow
- `POST /api/recommend` — deterministic recommendations by `workload_id` and `scale_level`
- `POST /api/recommend/natural` — natural-language recommendation flow (rate-limited)
- `POST /api/auth/register` / `POST /api/auth/login` / `POST /api/auth/logout` / `GET /api/auth/me`
- `POST /api/profiles`, `GET /api/profiles`, `PATCH /api/profiles/:id`, `DELETE /api/profiles/:id`

## Notes

- Authentication is cookie/session-based (`credentials: include` on frontend requests).
- This project is a personal learning project and not an official Dell product.
