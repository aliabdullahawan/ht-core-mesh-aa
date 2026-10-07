"""Role-based data access. Every route goes through these, so the rules live in one place."""
from fastapi import HTTPException

PROJECT_SELECT = """
select p.id, p.name, p.client_name, p.description, p.deadline,
       m.id as manager_id, m.name as manager_name,
       (select count(*) from tasks t where t.project_id = p.id {task_filter}) as task_count
from projects p
join users m on m.id = p.manager_id
"""


def _project_row(r: dict) -> dict:
    return {
        "id": str(r["id"]),
        "name": r["name"],
        "clientName": r["client_name"],
        "description": r["description"] or "",
        "deadline": r["deadline"].isoformat(),
        "manager": {"id": r["manager_id"], "name": r["manager_name"]},
        "taskCount": r["task_count"],
    }


def _task_row(r: dict) -> dict:
    return {
        "id": str(r["id"]),
        "title": r["title"],
        "description": r["description"] or "",
        "deadline": r["deadline"].isoformat(),
        "estimatedHours": float(r["estimated_hours"]),
        "assignee": {"id": r["assignee_id"], "name": r["assignee_name"]},
    }


def _project_query(user: dict, project_id: str | None = None) -> tuple[str, list]:
    role, uid = user["role"], user["id"]
    where, params = ["true"], []
    if role == "ADMIN":
        sql = PROJECT_SELECT.format(task_filter="")
    elif role == "MANAGER":
        sql = PROJECT_SELECT.format(task_filter="")
        where.append("p.manager_id = %s")
        params.append(uid)
    else:
        # AGENT: only projects containing their tasks; taskCount counts only their own tasks
        sql = PROJECT_SELECT.format(task_filter="and t.assignee_id = %s")
        params.append(uid)
        where.append("exists (select 1 from tasks t2 where t2.project_id = p.id and t2.assignee_id = %s)")
        params.append(uid)
    if project_id is not None:
        where.append("p.id::text = %s")
        params.append(project_id)
    return f"{sql} where {' and '.join(where)}", params


def get_projects(conn, user: dict) -> list[dict]:
    sql, params = _project_query(user)
    rows = conn.execute(sql + " order by p.deadline, p.name", params).fetchall()
    return [_project_row(r) for r in rows]


def get_tasks(conn, user: dict, project_id: str) -> list[dict]:
    sql = """
        select t.id, t.title, t.description, t.deadline, t.estimated_hours,
               a.id as assignee_id, a.name as assignee_name
        from tasks t join users a on a.id = t.assignee_id
        where t.project_id = %s
    """
    params = [project_id]
    if user["role"] == "AGENT":
        sql += " and t.assignee_id = %s"
        params.append(user["id"])
    elif user["role"] == "MANAGER":
        sql += " and exists (select 1 from projects p where p.id = t.project_id and p.manager_id = %s)"
        params.append(user["id"])
    rows = conn.execute(sql + " order by t.deadline, t.title", params).fetchall()
    return [_task_row(r) for r in rows]


def get_project_by_id(conn, user: dict, project_id: str) -> dict:
    sql, params = _project_query(user, project_id)
    row = conn.execute(sql, params).fetchone()
    if not row:
        # 404 (not 403) so users can't tell whether someone else's project exists
        raise HTTPException(404, "Project not found")
    project = _project_row(row)
    project["tasks"] = get_tasks(conn, user, project["id"])
    return project


def get_my_tasks(conn, user: dict) -> list[dict]:
    rows = conn.execute(
        """
        select t.id, t.title, t.description, t.deadline, t.estimated_hours,
               p.id as project_id, p.name as project_name, m.name as manager_name
        from tasks t
        join projects p on p.id = t.project_id
        join users m on m.id = p.manager_id
        where t.assignee_id = %s
        order by t.deadline, t.title
        """,
        (user["id"],),
    ).fetchall()
    return [
        {
            "id": str(r["id"]),
            "title": r["title"],
            "description": r["description"] or "",
            "deadline": r["deadline"].isoformat(),
            "estimatedHours": float(r["estimated_hours"]),
            "project": {"id": str(r["project_id"]), "name": r["project_name"], "managerName": r["manager_name"]},
        }
        for r in rows
    ]


def get_users(conn) -> list[dict]:
    # Never select password_hash here
    return conn.execute(
        """
        select id, name, role, specialization, skills from users
        order by case role when 'ADMIN' then 0 when 'MANAGER' then 1 else 2 end, id
        """
    ).fetchall()
