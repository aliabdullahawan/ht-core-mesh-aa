# Infinity Hack '26 — Step-by-Step Build Guide

**Challenge:** AI Project Manager — Meeting to Execution
**Flow we must demo:** Login → Paste meeting → AI creates projects/tasks → View saved results, filtered by role

| | **Huzaifa** — Backend & Data | **Ali** — AI & Frontend |
|---|---|---|
| Owns | Database, seeder, login, access control, validation + save, backend deploy | AI extraction, all screens, frontend deploy |
| Shared | Phase 0 contract, integration, testing, README, demo | Phase 0 contract, integration, testing, README, demo |

> **Name clash:** the demo data also has an "Ali" (Ali Raza, `DEV01`). In this guide, **"Ali"** means our teammate; the demo user is always written **"Ali Raza (DEV01)"**.

> **Team size:** the rulebook says teams must have exactly 4 registered participants. Confirm with organizers that a 2-person team is accepted.

---

## Rules to keep in mind the whole time

- Don't write code before the problem is officially announced. Accounts and keys can be ready beforehand.
- AI tools are allowed, but judges can question **either of us on any part**. Read the other person's code before the demo.
- Only the two of us touch the project. No help from friends or other teams.
- API keys live in `.env` only. Never commit them.
- Coding stops when time ends. Continuing is a disqualification offense.
- Live demo is mandatory. README.md is required for evaluation.
- Do **not** build: signup, forgot password, user management, cost calculation, progress tracking, charts.

---

## Before the clock starts (accounts only, no code)

| Step | Who | Done when |
|---|---|---|
| Python 3.11+, Node 20+, Git installed | Both | `python --version` and `node --version` work |
| OpenRouter account + API key; pick a primary and a backup model | Ali | Key saved privately |
| Supabase account | Huzaifa | Can log into dashboard |
| GitHub account access for both | Both | Both can push |
| Postman or curl available | Both | For testing access rules |

---

## Phase 0 — Setup & contract (0:00–0:15) · BOTH TOGETHER

This phase lets both of us build in parallel without waiting on each other. Do not skip it.

**Step 0.1 — Repo (Huzaifa)**
Create the GitHub repo with this structure and push it:

```
/backend
  main.py         # FastAPI app, CORS, all routes
  db.py           # database connection
  auth.py         # password hashing, JWT, get_current_user, require_admin
  access.py       # get_projects, get_tasks, get_project_by_id
  schemas.py      # Pydantic models (the shared contract)
  ai_extract.py   # Ali's AI module
  save.py         # validate + transactional save
  seed.py         # demo users
  schema.sql      # table definitions
  requirements.txt
  .env.example
/frontend         # Next.js app (Ali)
CONTRACT.md
README.md
.gitignore        # must include .env, node_modules, __pycache__, .venv
```

**Step 0.2 — Supabase project (Huzaifa)**
Create the project. Copy the **pooler** connection string (Project Settings → Database). Share it privately with Ali, not in Git.

**Step 0.3 — Test the AI key (Ali)**
Send one test request to OpenRouter and confirm a response comes back.

**Step 0.4 — Agree environment variables (Both)**
Write this into `backend/.env.example` and `frontend/.env.example`:

```
# backend/.env.example
DATABASE_URL=postgresql://user:password@host:6543/postgres
OPENROUTER_API_KEY=your-key-here
AI_MODEL=primary-model-id
AI_BACKUP_MODEL=backup-model-id
JWT_SECRET=any-long-random-string
FRONTEND_URL=http://localhost:3000

# frontend/.env.example
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Only `NEXT_PUBLIC_API_URL` goes in the frontend. The AI key and database URL stay backend-only.

**Step 0.5 — Write `backend/schemas.py` together (Both)**
These models are the contract between Ali's AI module and Huzaifa's save function.

```python
from datetime import date
from pydantic import BaseModel, Field

class DraftTask(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    assigneeId: str                       # must be a DEVxx id
    deadline: date                        # "2026-10-12" is parsed to a date
    estimatedHours: float = Field(gt=0)   # must be positive

class DraftProject(BaseModel):
    name: str = Field(min_length=1)
    clientName: str = Field(min_length=1)
    description: str = ""
    managerId: str                        # must be a PMxx id
    deadline: date
    tasks: list[DraftTask] = Field(min_length=1)

class Draft(BaseModel):
    projects: list[DraftProject] = Field(min_length=1)
```

**Step 0.6 — Write `CONTRACT.md` together (Both)**
Copy the API table below into it. Don't change a route or response shape without telling the other person.

| Method | Route | Who can call | Success response | Errors |
|---|---|---|---|---|
| POST | `/auth/login` | anyone | `{ token, user: { id, name, role } }` | 401 `{ detail: "Invalid email or password" }` |
| GET | `/me` | logged in | `{ id, name, role, specialization }` | 401 |
| GET | `/users` | logged in | `[{ id, name, role, specialization, skills }]` | 401 |
| GET | `/projects` | logged in | `[{ id, name, clientName, description, deadline, manager: { id, name }, taskCount }]` | 401 |
| GET | `/projects/{id}` | logged in | `{ ...project, manager: { id, name }, tasks: [{ id, title, description, deadline, estimatedHours, assignee: { id, name } }] }` | 401, 404 if not allowed |
| GET | `/tasks/mine` | agent | `[{ id, title, description, deadline, estimatedHours, project: { id, name, managerName } }]` | 401, 403 |
| POST | `/transcript` | admin | `{ projects: [{ id, name, taskCount }] }` | 403, 422 `{ errors: ["readable message", ...] }`, 502 if AI fails |
| POST | `/admin/reset` | admin | `{ ok: true }` | 403 |

**Key decision:** user IDs in the database are the demo references (`ADMIN`, `PM01`–`PM03`, `DEV01`–`DEV06`). The AI returns these same IDs, so no name matching is needed. Project and task IDs are generated by the database.

**Phase 0 done when:** repo exists, both have `.env` filled locally, `schemas.py` and `CONTRACT.md` are pushed.

---

## Phase 1 — Parallel build (0:15–1:30)

### Huzaifa — Backend & Data

**Step H1 — Install backend dependencies (5 min)**
```
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (Mac/Linux: source .venv/bin/activate)
pip install fastapi uvicorn "psycopg[binary]" bcrypt pyjwt python-dotenv httpx
pip freeze > requirements.txt
```
Done when: `uvicorn main:app --reload` starts with an empty app.

**Step H2 — Create tables (5 min)**
Put this in `schema.sql` and run it in the Supabase SQL editor:

```sql
create table users (
  id text primary key,                       -- ADMIN, PM01, DEV01 ...
  name text not null,
  email text not null unique,
  password_hash text not null,
  role text not null check (role in ('ADMIN','MANAGER','AGENT')),
  specialization text,
  skills text[] default '{}'
);

create table projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  client_name text not null,
  description text default '',
  manager_id text not null references users(id),
  deadline date not null,
  created_at timestamptz default now()
);

create table tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  title text not null,
  description text default '',
  assignee_id text not null references users(id),
  deadline date not null,
  estimated_hours numeric not null check (estimated_hours > 0)
);
```
Done when: three tables are visible in the Supabase Table Editor.

**Step H3 — Database connection + CORS (5 min)**
- `db.py`: a function that returns a `psycopg` connection using `DATABASE_URL`.
- `main.py`: add CORS so the browser allows the frontend on port 3000 to call the backend on port 8000:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Done when: server starts and connects without errors.

**Step H4 — Seeder (10 min)**
In `seed.py`, loop over the 10 demo accounts (Section 3 of the problem statement) and run, for each:

```sql
insert into users (id, name, email, password_hash, role, specialization, skills)
values (%s, %s, %s, %s, %s, %s, %s)
on conflict (email) do update set
  name = excluded.name, role = excluded.role,
  specialization = excluded.specialization, skills = excluded.skills,
  password_hash = excluded.password_hash;
```
Hash `Demo123!` with `bcrypt.hashpw(...)` before inserting.
Done when: `python seed.py` run **twice** still leaves exactly 10 rows.

**Step H5 — Login + auth dependencies (15 min)**
In `auth.py`:
- `POST /auth/login`: find user by email, check password with `bcrypt.checkpw`. Return the **same** 401 message for wrong email and wrong password. On success, return a JWT containing only the user's `id`, plus the user info.
- `get_current_user`: read the `Authorization: Bearer <token>` header, decode the JWT, load the user from the database. Raise 401 if invalid.
- `require_admin`: depends on `get_current_user`; raise 403 if role is not ADMIN.

Never read the role or user ID from the URL or request body. Always from the token.
Done when: login as `admin@novaworks.example` / `Demo123!` returns a token, and `GET /me` with that token returns the admin.

**Step H6 — Access-control functions (15 min)**
In `access.py`, write these once and reuse them in every route. Always join `users` so responses include **names**, not just IDs.

- `get_projects(user)`
  - ADMIN → all projects
  - MANAGER → `where p.manager_id = user.id`
  - AGENT → `select distinct p.* from projects p join tasks t on t.project_id = p.id where t.assignee_id = user.id`
- `get_tasks(user, project_id)`
  - ADMIN → all tasks in the project
  - MANAGER → all tasks, only if they manage that project
  - AGENT → only tasks where `assignee_id = user.id`
- `get_project_by_id(user, project_id)` → if the project isn't in `get_projects(user)`, raise 404; otherwise return it with `get_tasks(user, project_id)`

Wire up `/me`, `/users` (never return `password_hash`), `/projects`, `/projects/{id}`, `/tasks/mine` (403 if not an agent).
Done when: routes return correct shapes per `CONTRACT.md` (empty lists for now are fine).

**Step H7 — Validate + save (15 min)**
In `save.py`, write `save_draft(draft: Draft) -> list[str] | list[dict]`:

1. Load all users into a dict `{id: role}`.
2. For each project, check: `managerId` exists **and** has role MANAGER.
3. For each task, check: `assigneeId` exists **and** has role AGENT; task `deadline <= project deadline`.
4. Collect every problem as a readable string, e.g. `"QuickServe Mobile App / Mobile integration and testing: assignee DEV09 is not an agent"`.
5. If any errors → return them and **save nothing**.
6. If valid → inside `with conn.transaction():` insert each project (`returning id`), then its tasks using that id. If anything fails inside, the whole transaction rolls back automatically.
7. Return the created projects with task counts.

(Pydantic in `schemas.py` already handles missing fields, bad dates, and non-positive hours.)

Test it now with a hand-written `Draft` containing one project and two tasks. Don't wait for the AI.
Done when: a valid draft saves; a draft with a fake assignee returns an error and saves nothing.

**Step H8 — Reset route (5 min, optional)**
`POST /admin/reset` (admin only): `delete from projects` (tasks cascade). Users stay.

---

### Ali — AI & Frontend

**Step A1 — AI extraction module (25 min)**
In `backend/ai_extract.py`, write `extract(transcript: str, directory: list[dict]) -> Draft`:

1. Build the directory text from users with **only** `id, name, role, specialization, skills`. Never passwords or hashes.
2. Call `https://openrouter.ai/api/v1/chat/completions` with `httpx`, `timeout=60`, `temperature=0`, header `Authorization: Bearer <OPENROUTER_API_KEY>`. Request JSON output (`response_format: {"type": "json_object"}`) if the model supports it.
3. If the call fails or times out, retry once with `AI_BACKUP_MODEL`.
4. Strip any ```` ```json ```` fences, then `json.loads`.
5. Parse with `Draft.model_validate(data)`. If Pydantic raises `ValidationError`, convert its errors into readable strings and raise them so the route can return 422.

System prompt template:

```
You convert a company meeting transcript into projects and tasks.

Meeting date: 2026-10-07. All dates are in 2026. Output dates as YYYY-MM-DD.

Team directory (the ONLY people you may assign):
{directory as one line per person: id | name | role | specialization | skills}

Rules:
- Use only the FINAL agreed decisions. Later corrections replace earlier values
  (dates, hours, owners). The final recap is authoritative.
- Do not create tasks for features that were rejected or excluded.
- Each project's managerId must be a MANAGER id from the directory.
- Each task's assigneeId must be an AGENT id from the directory.
- Never invent people. Client contacts and end users are not employees.
- estimatedHours is developer effort in hours, not calendar days.
- Keep separate tasks separate, even if the same person owns them.
- If required information is missing, still return your best structure and
  leave the unknown field empty rather than guessing a person.

Return ONLY JSON in exactly this shape, no markdown, no explanation:
{"projects":[{"name":"","clientName":"","description":"","managerId":"",
"deadline":"YYYY-MM-DD","tasks":[{"title":"","description":"","assigneeId":"",
"deadline":"YYYY-MM-DD","estimatedHours":0}]}]}
```

6. Test standalone (a small `if __name__ == "__main__":` block) on the supplied transcript.

Done when: output matches the answer key: 3 projects, 12 tasks, UrbanCart deadline 2026-10-20, QuickServe integration 10 hours, HelpDeskPro testing owner Maryam (DEV06), no payment/maps/inventory/email tasks, no Kamran.

**Step A2 — Frontend setup (5 min)**
```
npx create-next-app@latest frontend
cd frontend
npm run dev
```
Done when: the starter page opens at `http://localhost:3000`.

**Step A3 — API helper + mock data (10 min)**
- `lib/api.ts`: one `apiFetch(path, options)` function that adds `Authorization: Bearer <token>` from `localStorage`, and redirects to `/login` on a 401 response.
- `lib/mock.ts`: fake data matching `CONTRACT.md` shapes exactly. Use it until Huzaifa's endpoints are ready.

**Step A4 — Login page `/login` (10 min)**
Email + password form. On success: save token and user to `localStorage`, then redirect by role:
- ADMIN → `/projects`
- MANAGER → `/projects`
- AGENT → `/my-tasks`

On failure: show "Invalid email or password".

**Step A5 — Shared layout + route guard (5 min)**
Top bar with the user's name, role, nav links (Projects / My Tasks / Team, shown by role) and a Logout button that clears `localStorage`. Any page opened without a token redirects to `/login`.

**Step A6 — Projects list `/projects` (10 min)**
Project cards: name, client, manager name, deadline, task count. If role is ADMIN, show a **Create from Transcript** button. The backend decides which projects appear, so one page serves admin and managers.

**Step A7 — Project detail `/projects/[id]` (10 min)**
Header: name, client, manager name, deadline, description.
Task table: title, description, assignee name, deadline, estimated hours.
On 404: show "Project not found or you don't have access."

**Step A8 — Create from Transcript `/transcript` (15 min)**
- Large textarea and a **Create from Transcript** button.
- Button **disabled while processing** (prevents duplicate projects).
- Loading text: "AI is reading the meeting…"
- Success: "Created 3 projects and 12 tasks" with links to each project.
- 422: show the error list and **keep the transcript in the box** so the admin can fix it and resubmit.
- 502 or network error: "AI service failed, please try again."
- Empty textarea: don't submit.

**Step A9 — My Tasks `/my-tasks` and Team `/team` (10 min)**
- My Tasks: task rows with project name and manager name.
- Team: read-only table of names, roles, and specializations.

---

### Check-in at 0:50 (5 min, both)

- Huzaifa: are login and `/projects` returning real data?
- Ali: does `extract()` produce the correct 12 tasks?
- Fix any contract mismatch now, not at 1:30.

---

## Phase 2 — Integration (1:30–2:15)

**Step I1 — Transcript route (Huzaifa, 15 min)**
In `main.py`, `POST /transcript`:
1. `require_admin`
2. Reject empty transcript → 422 `{ errors: ["Transcript is empty"] }`
3. Load directory from `users` (no password hashes)
4. Call Ali's `extract()`: AI failure → 502; Pydantic errors → 422 with readable list
5. Call `save_draft()`: errors → 422; success → 200 with created projects

**Step I2 — Switch frontend to real API (Ali, 15 min)**
Replace mock data with `apiFetch` calls on every page. Check every screen with real responses.

**Step I3 — Full flow together (Both, 15 min)**
Login as admin → paste supplied transcript → create → open each project → log in as Ayesha, Ali Raza (DEV01), Hamza. Fix whatever breaks.

**Step I4 — 2:15 decision (Both)**
- Core flow works → Huzaifa starts deploying (Phase 4) while Ali starts testing.
- Core flow broken → both keep fixing; stay local and rely on the demo video.

---

## Phase 3 — Testing (2:15–2:40)

Each person tests the **other's** work. This also prepares us to explain it to judges.

**Huzaifa tests (AI + frontend):**
- [ ] Supplied transcript → exactly 3 projects, 12 tasks
- [ ] UrbanCart deadline 2026-10-20 (not 18) · integration task 2026-10-19 (not 17)
- [ ] QuickServe integration 10 hours (not 8)
- [ ] HelpDeskPro testing owner Maryam (not Zain)
- [ ] No payment / inventory / maps / email tasks · Kamran not assigned
- [ ] Reset, then changed transcript: QuickServe integration → 12 hours, 23 October. Only that task changes
- [ ] Loading state, success message, and error list all display
- [ ] Button can't be double-clicked during processing

**Ali tests (backend + access):**
- [ ] Ayesha sees only UrbanCart
- [ ] Ali Raza (DEV01) sees only his 3 UrbanCart tasks, never Hamza's
- [ ] Hamza sees 2 tasks across UrbanCart and QuickServe
- [ ] Direct request with Ali Raza's token to QuickServe → 404:
  `curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/projects/<QUICKSERVE_ID>`
- [ ] Non-admin `POST /transcript` → 403
- [ ] No token → 401
- [ ] Refresh browser → data still there
- [ ] `python seed.py` twice → still 10 users
- [ ] `/users` response contains no password hashes

---

## Phase 4 — Deploy, submit, demo prep (2:40–3:00)

| Step | Who | Details |
|---|---|---|
| Deploy backend | Huzaifa | Render web service. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set backend env vars. Use Supabase **pooler** URL. Set `FRONTEND_URL` to the Vercel URL |
| Deploy frontend | Ali | Vercel, root directory `frontend`. Set `NEXT_PUBLIC_API_URL` to the Render URL |
| Seed deployed DB | Huzaifa | Same Supabase DB, so already seeded. Confirm login works live |
| README: setup, run, seed commands, env vars, deployment steps | Huzaifa | Fill the provided template |
| README: what works, demo accounts, judge test steps, known limitations | Ali | Mention Render free-tier cold start if deployed |
| Demo video (backup) | Ali | Follow problem statement Section 8 steps |
| Check no secrets in Git; `.env.example` has placeholders | Huzaifa | `git log` check |
| Final commit and push | Both | Before time ends |

**Knowledge swap (5 min):** Huzaifa explains auth, access control, and the transaction to Ali. Ali explains the prompt, parsing, and frontend flow to Huzaifa.

### Live demo script
1. **Problem:** meeting decisions get typed into tools by hand; slow and error-prone
2. Seeded users, no signup
3. Admin pastes transcript → Create → 3 projects, 12 tasks
4. Open UrbanCart: client, manager, deadline, tasks with owners and hours
5. Log in as Ayesha, Ali Raza (DEV01), and Hamza: role-based views
6. Direct API request blocked (curl/Postman)
7. Refresh → data persists
8. Modified transcript → output changes (real AI, not hardcoded)
9. **Where AI is used:** extraction with directory-constrained assignment, validated before an all-or-nothing save
10. **Next with more time:** editing tasks, re-processing follow-up meetings, field-level correction of AI errors

---

## If time runs short — cut in this order

1. Deployment (stay local, use the demo video)
2. `/admin/reset` (delete rows in the Supabase dashboard instead)
3. Team page styling
4. Backup AI model

**Never cut:** login, transcript → saved records, backend role filtering, persistence, README.
