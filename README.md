# SmartMark — Multi-Tenant School Marks Management System

A multi-tenant SaaS marks-management system for schools running Kenya's CBC
curriculum (Playgroup–Grade 10). Every school that signs up gets its own
isolated tenant — its own students, teachers, marks and branding — under one
shared codebase. **No school name, domain, or branding is hardcoded
anywhere**, and **no seed/demo data is created** — every school starts
completely empty and the admin builds it up from scratch.

This was built directly from two specs: the invitation/account-activation
workflow doc and the full marks-management product spec. See
`WHATS_BUILT.md` for a checklist of what's implemented vs. what's stubbed
for a follow-up pass.

## Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate (Alembic), Flask-JWT-Extended, PostgreSQL
- **Frontend:** React 18, Vite, React Router, Tailwind CSS, Recharts
- **Auth:** JWT (access + refresh), bcrypt password hashing
- **Excel:** openpyxl (marklist export, CSV student import)

## Project layout

```
smartmark/
  backend/          Flask API
    app/
      models/        SQLAlchemy models (all tenant-scoped by school_id)
      routes/         Blueprints — auth, invitations, academics, users, exams, marks, reports, dashboard
      utils/          security, identity (email generation), auth/RBAC, mailer, audit
    run.py
    requirements.txt
    .env.example
  frontend/         React + Vite app
    src/
      pages/          One file per screen
      components/     AppShell (nav), ReportCardView, ProtectedRoute, ui.jsx (design system primitives)
      context/         AuthContext
      api/             fetch client with JWT handling
```

## Running it locally

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set a real SECRET_KEY / JWT_SECRET_KEY, and DATABASE_URL to your Postgres instance.
# For a quick local trial without Postgres, DATABASE_URL=sqlite:///smartmark_dev.db also works.

export $(cat .env | xargs)   # or use python-dotenv / your process manager
flask db init                # first time only
flask db migrate -m "initial schema"
flask db upgrade

python run.py                # runs on http://localhost:5000
```

Invitation emails default to the **console** mail backend — they're printed
to the server log instead of actually sent, so you can test the whole
invite → accept → activate flow without configuring SMTP. Set
`MAIL_BACKEND=smtp` and the `SMTP_*` variables in `.env` to send real email.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                  # runs on http://localhost:5173, proxies /api to :5000
```

Open `http://localhost:5173/register-school` to create your first school.
There is deliberately no seed data — you'll land in an empty dashboard and
build up grades, streams, subjects, teachers and students from there.

## Multi-tenancy & security notes

- Every tenant-scoped table carries a `school_id` column, and **every**
  route reads/writes through `scoped(Model)` (see `app/utils/auth.py`),
  which filters by the `school_id` embedded in the verified JWT — never
  from a client-supplied parameter. A second school's data is provably
  unreachable (covered by the test flow described below).
- A user's `personal_email` (for invitation delivery) and `smartmark_email`
  (their login identity) are stored as separate fields, exactly per the
  invitation spec. Name normalization + a numeric-suffix collision strategy
  guarantee the generated login email is always unique and never overwrites
  an existing account.
- Invitation tokens are cryptographically random (`secrets.token_urlsafe`),
  only their SHA-256 hash is stored, and they're single-use, expiring
  (default 48h, configurable per school) and revocable (cancel/resend).
- Teachers can only read/write marks for grade/stream/subject combinations
  an admin has explicitly assigned to them via `TeacherAssignment` — this is
  enforced server-side in `app/routes/marks.py`, not just hidden in the UI.
- Passwords are bcrypt-hashed; nothing sensitive (passwords, raw tokens) is
  ever logged or returned in API responses.

I ran a full in-process integration test covering: school registration →
grade/stream/subject creation → teacher invitation → accept & password
creation → **marks entry blocked until assignment (403)** → admin assigns
teacher → student invitation & activation → marks entry succeeds → marklist
ranks correctly → a second school registers and **cannot see the first
school's grades**. All steps passed.

## Deployment

- Backend: any WSGI host (gunicorn is included in requirements.txt) behind
  a reverse proxy; point `DATABASE_URL` at managed Postgres, set real
  `SECRET_KEY`/`JWT_SECRET_KEY`, set `FRONTEND_BASE_URL` to your deployed
  frontend origin (used to build invitation/report links), and configure
  `MAIL_BACKEND=smtp` with real SMTP credentials.
- Frontend: `npm run build` produces `dist/` — deploy as a static site
  (Netlify, Vercel, S3+CloudFront, etc.) and point it at your API origin
  (update the `/api` proxy target or set an `VITE_API_BASE` env + small
  client tweak if the API isn't same-origin).
- File storage (crests/logos/student photos) and real email are pluggable
  via `STORAGE_BACKEND` / `MAIL_BACKEND` in `backend/app/config.py` — swap
  in S3/Cloudinary and a real SMTP/transactional-email provider for
  production.
