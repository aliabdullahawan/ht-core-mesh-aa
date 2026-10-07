# NovaWorks PM - AI Meeting to Project CRM

Infinity Hack '26 · AI Project Manager challenge. An admin pastes a meeting transcript, AI turns it into projects and tasks assigned to the real team, and everyone logs in to see only the work they are allowed to see.

## Team
- Team name: [team name]
- Huzaifa Rao: backend, database, auth, access control, validation and save, backend deploy
- Ali: AI extraction, frontend screens, frontend deploy
- Repository: [GitHub URL]

## What Works
- **Seeded login.** There are ten demo accounts and no signup. Sessions use a JWT.
- **Admin.** Sees all project cards, the team directory and **Create from Transcript**:
  - Paste a meeting (or click *Load sample transcript*) and AI extracts the projects and tasks.
  - The result is validated against the directory and saved in one transaction.
- **Manager.** Sees only the projects they manage, with all of those projects' tasks.
- **Agent.** *My Tasks* lists only their own tasks. They can open the related project, but only their own tasks appear in it.
- **Access is enforced by the backend** on every request, not just by hiding buttons:
  - A direct request for someone else's project returns 404.
  - Non-admin access to transcript creation returns 403.
- **Validation errors save nothing.** Examples are an unknown or wrong-role person, a task deadline after the project deadline, a missing field or non-positive hours. The admin sees a readable error list and the transcript stays in the box to correct and resubmit.
- **Data persists** in hosted PostgreSQL and survives refresh and restarts.

## Technology Stack
- Frontend: Next.js 16 (App Router, React 19, TypeScript)
- Backend: Python 3.11+ · FastAPI · psycopg 3 (with a connection pool)
- Database: PostgreSQL 17 on Supabase
- AI: Groq (OpenAI-compatible API), primary `openai/gpt-oss-120b`, backup `qwen/qwen3.8-27b`, `temperature=0`, strict JSON-schema output. OpenRouter also works by setting `AI_API_URL`.
- Auth: bcrypt password hashes. Login returns a JWT (12 h) holding only the user ID. The backend loads the user and role from the database on every request and never trusts a role or ID sent by the client.

## Links
- Live application: [URL or Not deployed]
- Demo video: [URL]

## Requirements
- Python 3.11+ and Node.js 20+
- A PostgreSQL database (Supabase pooler URL used here; any Postgres 13+ works)
- An OpenRouter API key

## Run Locally
Two terminals stay running: the backend on port 8000 and the frontend on port 3000.

```sh
git clone [YOUR_REPOSITORY_URL]
cd ht-core-mesh-aa
```

**Backend (terminal 1)**
```sh
cd backend
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env  (then fill in real values)
python seed.py --schema           # creates the tables and seeds the 10 demo users
uvicorn main:app --reload --port 8000
```
- `python seed.py` can be re-run at any time and upserts by email, so it never duplicates users.
- Alternatively, run `schema.sql` in the Supabase SQL editor and then run `python seed.py`.

**Frontend (terminal 2)**
```sh
cd frontend
npm install
copy .env.example .env.local      # macOS/Linux: cp .env.example .env.local
npm run dev
```
Open http://localhost:3000.

**Optional: check the AI on its own**
```sh
cd backend
python ai_extract.py              # runs the sample transcript and prints the extracted projects/tasks
```

## Environment Variables
| Variable | Purpose | Where configured |
| --- | --- | --- |
| `DATABASE_URL` | Postgres connection string (Supabase pooler, port 6543) | backend |
| `OPENROUTER_API_KEY` | AI provider key (a Groq `gsk_` key or an OpenRouter key) | backend only |
| `AI_API_URL` | Optional chat-completions URL (default: Groq for `gsk_` keys, otherwise OpenRouter) | backend |
| `AI_MODEL` | Primary OpenRouter model ID | backend |
| `AI_BACKUP_MODEL` | Model tried if the primary fails (optional) | backend |
| `JWT_SECRET` | Signs login tokens | backend |
| `FRONTEND_URL` | Allowed CORS origin(s), comma separated | backend |
| `NEXT_PUBLIC_API_URL` | Backend base URL | frontend |

Real values are kept out of Git. The `.env.example` files contain placeholders only.

## Demo Login Accounts
These emails are fictional identifiers, not real inboxes. The password for every account is `Demo123!`.

| Role | Name | Demo email |
| --- | --- | --- |
| Admin | Admin | admin@novaworks.example |
| Manager | Ayesha Khan | ayesha@novaworks.example |
| Manager | Bilal Ahmed | bilal@novaworks.example |
| Manager | Hina Malik | hina@novaworks.example |
| Agent | Ali Raza | ali@novaworks.example |
| Agent | Hamza Shah | hamza@novaworks.example |
| Agent | Sara Noor | sara@novaworks.example |
| Agent | Usman Tariq | usman@novaworks.example |
| Agent | Zain Abbas | zain@novaworks.example |
| Agent | Maryam Asif | maryam@novaworks.example |

## How Judges Can Test
1. Log in as admin and open **Create from Transcript**.
2. Click **Load sample transcript**, or paste the supplied transcript. The file is at `frontend/public/sample-transcript.txt`.
3. Click **Create from Transcript**. Expect **3 projects and 12 tasks**.
4. Open UrbanCart Website. Expect manager Ayesha Khan, deadline 20 Oct 2026, four tasks with owners and hours.
5. Log out and log in as **Ayesha**. Only UrbanCart should appear.
6. Log in as **Ali Raza**. *My Tasks* shows only his three UrbanCart tasks, and opening UrbanCart shows only those three.
7. Log in as **Hamza**. He has two API tasks, one in UrbanCart and one in QuickServe.
8. Request another user's project directly. Expect a 404:
   ```sh
   curl -H "Authorization: Bearer <ALI_TOKEN>" http://localhost:8000/projects/<QUICKSERVE_ID>
   ```
   A non-admin `POST /transcript` returns 403, and a request with no token returns 401.
9. Refresh the page. The data is still there.
10. Run a changed-input test:
    - As admin, run `POST /admin/reset` (or delete the projects in the database).
    - Edit the transcript so that QuickServe *Mobile integration and testing* is **12 hours, 23 October**, and resubmit.
    - Only that task should change.

## API
See [CONTRACT.md](CONTRACT.md) for every route, who can call it and its response shape.

## Deployment
- **Database:** Supabase Postgres. Use the **pooler** connection string, which is IPv4 friendly. Run `python seed.py --schema` once against it.
- **Backend:** Render web service.
  - Root directory: `backend`
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Set the backend environment variables. `FRONTEND_URL` should be the Vercel URL.
- **Frontend:** Vercel.
  - Root directory: `frontend`
  - Set `NEXT_PUBLIC_API_URL` to the Render URL.

## Known Limitations
- Created projects and tasks can't be edited in the UI. To re-run a transcript, reset first (`POST /admin/reset`) or the projects are created again.
- AI output can vary between models. Anything invalid is rejected with a readable list rather than saved, but a plausible-but-wrong value, such as the wrong hours, would still be saved.
- The Render free tier sleeps when idle, so the first request after a while can take about 30 seconds.
- The token is stored in `localStorage`. That is fine for a demo, but production would use httpOnly cookies.
