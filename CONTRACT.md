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