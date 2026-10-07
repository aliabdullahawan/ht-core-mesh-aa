"""Validate an AI draft against the real directory, then save it all-or-nothing."""
from schemas import Draft


def validate_draft(conn, draft: Draft) -> list[str]:
    roles = {r["id"]: r["role"] for r in conn.execute("select id, role from users").fetchall()}
    errors = []
    for p in draft.projects:
        label = p.name or "Unnamed project"
        if not p.managerId:
            errors.append(f"{label}: manager is missing")
        elif p.managerId not in roles:
            errors.append(f"{label}: manager {p.managerId} does not exist")
        elif roles[p.managerId] != "MANAGER":
            errors.append(f"{label}: {p.managerId} is not a manager")
        for t in p.tasks:
            tlabel = f"{label} / {t.title}"
            if not t.assigneeId:
                errors.append(f"{tlabel}: assignee is missing")
            elif t.assigneeId not in roles:
                errors.append(f"{tlabel}: assignee {t.assigneeId} does not exist")
            elif roles[t.assigneeId] != "AGENT":
                errors.append(f"{tlabel}: assignee {t.assigneeId} is not an agent")
            if t.deadline > p.deadline:
                errors.append(
                    f"{tlabel}: task deadline {t.deadline} is after the project deadline {p.deadline}"
                )
    return errors


def save_draft(conn, draft: Draft) -> tuple[list[str], list[dict]]:
    """Returns (errors, created). If errors is non-empty, nothing was saved."""
    errors = validate_draft(conn, draft)
    if errors:
        return errors, []
    created = []
    # Any exception inside rolls back every project and task in this draft
    with conn.transaction():
        for p in draft.projects:
            project_id = conn.execute(
                """insert into projects (name, client_name, description, manager_id, deadline)
                   values (%s, %s, %s, %s, %s) returning id""",
                (p.name, p.clientName, p.description, p.managerId, p.deadline),
            ).fetchone()["id"]
            for t in p.tasks:
                conn.execute(
                    """insert into tasks (project_id, title, description, assignee_id, deadline, estimated_hours)
                       values (%s, %s, %s, %s, %s, %s)""",
                    (project_id, t.title, t.description, t.assigneeId, t.deadline, t.estimatedHours),
                )
            created.append({"id": str(project_id), "name": p.name, "taskCount": len(p.tasks)})
    return [], created
