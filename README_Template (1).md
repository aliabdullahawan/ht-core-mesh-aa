# [Project Name] - AI Meeting to Project CRM

> Participant template: replace every bracketed placeholder with your actual project details. Commands below are placeholders, not commands for a specific stack. Save the completed file as `README.md` at your repository root.

## Team
- Team name: [name]
- Four members and responsibilities: [names and responsibilities]
- Repository: [GitHub URL]

## What Works
[Briefly describe the CRM, seeded login, admin transcript automation, manager project view, agent task view, and saved records. Mark incomplete features honestly.]

## Technology Stack
- Frontend: [framework and version]
- Backend: [framework/runtime and version]
- Database: [engine and version]
- AI: [provider and model]
- Authentication/session approach: [brief explanation]

## Links
- Live application: [URL or Not deployed]
- Demo video: [accessible recording URL; required for a local database]

## Requirements
[List runtime versions, package manager, database requirements, and AI API access needed.]

## Run Locally
1. Clone this repository and enter its directory:
   ```sh
   git clone [YOUR_REPOSITORY_URL]
   cd [YOUR_PROJECT_DIRECTORY]
   ```
2. Install dependencies: [exact commands; specify frontend/backend folders if separate].
3. Copy the provided `.env.example` to the configuration path your app uses.
4. Set environment variables listed below using local/private values.
5. Create/connect the database: [exact command/instructions].
6. Apply schema/migrations: [exact command].
7. Seed all ten demo users: [exact command]. Re-running should not duplicate users.
8. Start backend and frontend: [exact commands, ports, and local browser URL].

Include copy-and-paste commands for your chosen stack. Explain which terminals/processes must remain running.

## Environment Variables
| Variable | Purpose | Where configured |
| --- | --- | --- |
| [DATABASE_VARIABLE_NAME] | Database connection | [backend/local/deployment] |
| [AI_API_KEY_VARIABLE_NAME] | AI provider credential | [backend only] |
| [MODEL_VARIABLE_NAME, if used] | AI model selection | [backend] |
| [SESSION_VARIABLE_NAME, if used] | Session signing/secret | [backend] |
| [FRONTEND_API_URL, if used] | Backend endpoint | [frontend] |

List only variables actually used. Include `.env.example` with placeholders; never commit real API keys, database credentials, or session secrets. Do not put AI/database secrets in browser-exposed variables.

## Demo Login Accounts
These emails are fictional identifiers, not mailboxes. Signup, email verification, and forgot password are unnecessary.

| Role | Name | Demo email | Password |
| --- | --- | --- | --- |
| Admin | Admin | admin@novaworks.example | Demo123! |
| Manager | Ayesha Khan | ayesha@novaworks.example | Demo123! |
| Manager | Bilal Ahmed | bilal@novaworks.example | Demo123! |
| Manager | Hina Malik | hina@novaworks.example | Demo123! |
| Agent | Ali Raza | ali@novaworks.example | Demo123! |
| Agent | Hamza Shah | hamza@novaworks.example | Demo123! |
| Agent | Sara Noor | sara@novaworks.example | Demo123! |
| Agent | Usman Tariq | usman@novaworks.example | Demo123! |
| Agent | Zain Abbas | zain@novaworks.example | Demo123! |
| Agent | Maryam Asif | maryam@novaworks.example | Demo123! |

[Update this table if your submitted demo credentials differ. State when/how to run the seeder.]

## How Judges Can Test
1. Log in as admin; open Create from Transcript.
2. Paste the supplied meeting transcript: [file location or paste instructions].
3. Click create; expect three projects and twelve tasks.
4. Open UrbanCart: manager Ayesha, deadline 20 October 2026, four tasks.
5. Log out and log in as Ayesha: only her assigned project should appear.
6. Log in as Ali: only his three assigned UrbanCart tasks should appear.
7. Log in as Hamza: his two API tasks span UrbanCart and QuickServe.
8. Verify other users' projects/tasks cannot be fetched directly.
9. Refresh to verify persistence.
10. Test a modified transcript to check the AI flow responds to changed input.

[Explain how to reset generated demo projects/tasks between tests without deleting seeded users.]

## Deployment Details
- Deployment status: [Live / Local only]
- Frontend host: [provider, URL]
- Backend host: [provider, URL, or explain shared hosting]
- Database: [local engine or hosted provider such as Aiven; no credentials]
- Deployed branch/commit: [branch and commit SHA]

### How We Deployed
1. [Exact build command and output directory for the frontend.]
2. [Backend build/start command and service settings.]
3. [Database provision/connect instructions, including SSL if needed.]
4. [Environment-variable names configured on each platform, without values.]
5. [Schema/migration and seed commands run against the deployment database.]
6. [Frontend API URL and cross-origin configuration, if used.]
7. [How judges can log in and use AI on the live deployment.]

If the project is local only, state that here and provide the demo video. A GitHub repository alone is not a deployed application. A working live app with a hosted database is eligible for deployment bonus marks.

## Known Limitations
[State incomplete features, API quota issues, cold starts, or extra manual steps affecting evaluation.]

## Submission Summary
- Source repository: [URL]
- Live link or local demo video: [URL]
- Setup and seed commands: [documented above]
- Demo login accounts: [confirmed working]
- Features completed: [short list]
