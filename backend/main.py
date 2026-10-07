import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import access
import auth
from ai_extract import AIError, DraftInvalid, extract
from db import get_db
from save import save_draft

app = FastAPI(title="NovaWorks AI Project Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginBody(BaseModel):
    email: str
    password: str


class TranscriptBody(BaseModel):
    transcript: str = ""


def errors_response(errors: list[str]) -> JSONResponse:
    return JSONResponse(status_code=422, content={"errors": errors})


@app.get("/")
def health():
    return {"ok": True}


@app.post("/auth/login")
def login(body: LoginBody, conn=Depends(get_db)):
    return auth.login(conn, body.email, body.password)


@app.get("/me")
def me(user=Depends(auth.get_current_user)):
    return user


@app.get("/users")
def users(user=Depends(auth.get_current_user), conn=Depends(get_db)):
    return access.get_users(conn)


@app.get("/projects")
def projects(user=Depends(auth.get_current_user), conn=Depends(get_db)):
    return access.get_projects(conn, user)


@app.get("/projects/{project_id}")
def project_detail(project_id: str, user=Depends(auth.get_current_user), conn=Depends(get_db)):
    return access.get_project_by_id(conn, user, project_id)


@app.get("/tasks/mine")
def my_tasks(user=Depends(auth.get_current_user), conn=Depends(get_db)):
    if user["role"] != "AGENT":
        raise HTTPException(403, "Only agents have assigned tasks")
    return access.get_my_tasks(conn, user)


@app.post("/transcript")
def create_from_transcript(body: TranscriptBody, admin=Depends(auth.require_admin), conn=Depends(get_db)):
    if not body.transcript.strip():
        return errors_response(["Transcript is empty"])
    directory = access.get_users(conn)
    try:
        draft = extract(body.transcript, directory)
    except DraftInvalid as e:
        return errors_response(e.errors)
    except AIError as e:
        raise HTTPException(502, str(e))
    errors, created = save_draft(conn, draft)
    if errors:
        return errors_response(errors)
    return {"projects": created}


@app.post("/admin/reset")
def reset(admin=Depends(auth.require_admin), conn=Depends(get_db)):
    with conn.transaction():
        conn.execute("delete from projects")  # tasks cascade; users stay
    return {"ok": True}
