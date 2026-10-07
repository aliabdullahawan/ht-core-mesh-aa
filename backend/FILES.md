# Backend files: what each one does

A plain-language map of the `backend/` folder. Read this before the demo so either of us can answer a judge's question about any file.

## How a request flows

1. The browser sends a request to **main.py**.
2. **auth.py** checks the login token and works out who the user is.
3. **access.py** fetches only the data that user is allowed to see.
4. **db.py** provides the database connection used for all of this.

The transcript feature adds two steps: **ai_extract.py** asks the AI to turn the meeting into projects and tasks, and **save.py** checks that result and saves it.

---

## main.py: the front door
- Starts the web server (FastAPI) and lists every URL the frontend can call: login, me, users, projects, project detail, my tasks, transcript and reset.
- Each route only connects the pieces. It asks auth.py who the user is, then calls access.py, ai_extract.py or save.py to do the work.
- Sets up CORS, the browser rule that allows the frontend on port 3000 to talk to the backend on port 8000.
- Turns problems into the right error codes:
  - 401: not logged in
  - 403: not allowed
  - 404: not found or not yours
  - 422: the transcript or AI result has problems
  - 502: the AI service itself failed

## auth.py: login and identity
- **Login:** finds the user by email and checks the password against the stored bcrypt hash. Wrong email and wrong password give the same message, so nobody can tell which emails exist.
- **Token:** on success it returns a signed JWT that holds only the user's ID and expires after 12 hours.
- **Who is calling:** every protected request sends this token. auth.py verifies it and loads the user, including their role, fresh from the database.
- **Admin check:** stops anyone who isn't the admin with a 403.
- The user's identity and role always come from the token, never from anything the browser sends.

## access.py: who can see what
All the role rules live here, written once and reused by every route.
- **Projects list:**
  - The admin sees all projects.
  - A manager sees only the projects they manage.
  - An agent sees only projects that contain at least one task assigned to them.
- **Tasks inside a project:**
  - The admin and the project's manager see every task.
  - An agent sees only their own tasks, never a teammate's.
- **One project by ID:** if the project isn't in the user's allowed list, the answer is 404 (not 403), so users can't even confirm that someone else's project exists.
- **My tasks:** an agent's own tasks, with project name and manager name.
- **Team directory:** names, roles, specializations and skills. Password hashes are never included.

## ai_extract.py: the AI step
- Builds the instructions for the AI:
  - the meeting date;
  - the team directory, with only ID, name, role, specialization and skills, so no emails or passwords are sent;
  - the rules: use final decisions only, skip rejected features, never invent people, and keep separate tasks separate.
- Sends the transcript to the AI provider. That is Groq for our key (or OpenRouter), with temperature 0 so results are consistent.
- Asks the provider for strict structured output, so the reply comes back in exactly the projects-and-tasks shape we expect.
- **Reliability:**
  - If the main model fails or returns a bad shape, it tries the backup model.
  - If the provider says "too many requests", it waits briefly and retries once.
- Checks the reply against the shared contract in schemas.py. Problems become readable messages such as "Project / Task: deadline is missing".
- Can also be run on its own to test the AI against the sample transcript without the website.

## schemas.py: the shared contract
- Describes the exact shape of an AI result: a list of projects, each with name, client, description, manager ID, deadline and a list of tasks. Each task has title, description, assignee ID, deadline and estimated hours.
- Enforces the basic rules automatically: required text can't be empty, dates must be real dates, hours must be more than zero, and every project needs at least one task.
- This is the agreement between the AI part and the saving part, so neither side changes it without telling the other.

## save.py: validate, then save all-or-nothing
- **Checks the AI result against the real team:**
  - Every manager ID must exist and actually be a manager.
  - Every assignee must exist and actually be an agent.
  - No task can be due after its project's deadline.
- Collects every problem into a readable list. If there's even one problem, **nothing is saved**, and the admin sees the list and can fix the transcript.
- If everything is valid, it saves all projects and their tasks inside one database transaction. If anything goes wrong mid-way, the whole save is undone, so there are never half-created projects.
- Returns the created projects with their task counts for the success message.

## db.py: database connection
- Reads the database address from the environment and connects to PostgreSQL on Supabase.
- Keeps a small pool of open connections. Our database is far away, so opening a fresh one each time took about 4 seconds, and reusing them makes pages fast.
- Uses settings the Supabase connection pooler needs, and makes sure the all-or-nothing save in save.py is a real transaction.
- Also offers a one-off connection for scripts such as the seeder.

## seed.py: demo accounts
- Creates the ten demo users from the challenge: 1 admin, 3 managers and 6 agents, all with the password Demo123!. Passwords are stored as bcrypt hashes, never as plain text.
- Safe to run as many times as you like. It updates users by email instead of adding duplicates, so there are always exactly 10.
- With the schema option, it creates the database tables first, which is handy on a brand-new database.

## schema.sql: the database tables
- **users:** ID (such as ADMIN, PM01, DEV01), name, unique email, password hash, role (ADMIN, MANAGER or AGENT), specialization and skills.
- **projects:** auto-generated ID, name, client, description, manager (must be a real user), deadline and creation time.
- **tasks:** auto-generated ID, parent project, title, description, assignee (must be a real user), deadline and estimated hours (must be above zero).
- Deleting a project deletes its tasks automatically, which the reset button relies on.
- Includes indexes so lookups by project, assignee and manager stay fast.

## requirements.txt: Python packages
The list of libraries the backend needs, installed with one pip command:
- the web framework and server;
- the PostgreSQL driver and connection pool;
- password hashing and login tokens;
- environment-file loading;
- the HTTP client used to call the AI;
- data validation.

## .env.example: settings template
- Lists every setting the backend needs, with placeholder values: database address, AI key, AI model and backup model, optional AI URL, token secret and frontend address.
- Copy it to `.env` and fill in real values. The real `.env` is never committed to GitHub because it holds secrets.

## .env: real settings (not in GitHub)
- Your private copy with the real database password, AI key and token secret.
- After changing it, restart the backend, because auto-reload only notices changes to code files.

## FILES.md
- This guide.
