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