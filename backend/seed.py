"""Seed the ten demo users. Safe to re-run: upserts by email.

    python seed.py            # seed users
    python seed.py --schema   # create tables first, then seed
"""
import sys
from pathlib import Path

import bcrypt

from db import connect

PASSWORD = "Demo123!"

USERS = [
    ("ADMIN", "Admin", "admin@novaworks.example", "ADMIN", "Administrator", ["Company overview", "transcript creation"]),
    ("PM01", "Ayesha Khan", "ayesha@novaworks.example", "MANAGER", "Web PM", ["Web projects", "client coordination"]),
    ("PM02", "Bilal Ahmed", "bilal@novaworks.example", "MANAGER", "Mobile PM", ["Mobile projects", "delivery planning"]),
    ("PM03", "Hina Malik", "hina@novaworks.example", "MANAGER", "AI PM", ["AI projects", "requirement review"]),
    ("DEV01", "Ali Raza", "ali@novaworks.example", "AGENT", "Full-Stack", ["React", "frontend integration"]),
    ("DEV02", "Hamza Shah", "hamza@novaworks.example", "AGENT", "Full-Stack", ["Node.js", "databases", "APIs"]),
    ("DEV03", "Sara Noor", "sara@novaworks.example", "AGENT", "App Developer", ["Flutter", "mobile UI"]),
    ("DEV04", "Usman Tariq", "usman@novaworks.example", "AGENT", "App Developer", ["Flutter", "integration", "testing"]),
    ("DEV05", "Zain Abbas", "zain@novaworks.example", "AGENT", "AI Developer", ["LLMs", "extraction", "prompts"]),
    ("DEV06", "Maryam Asif", "maryam@novaworks.example", "AGENT", "AI Developer", ["Retrieval", "document processing"]),
]

UPSERT = """
insert into users (id, name, email, password_hash, role, specialization, skills)
values (%s, %s, %s, %s, %s, %s, %s)
on conflict (email) do update set
  name = excluded.name, role = excluded.role,
  specialization = excluded.specialization, skills = excluded.skills,
  password_hash = excluded.password_hash
"""


def main():
    with connect() as conn:
        if "--schema" in sys.argv:
            conn.execute((Path(__file__).parent / "schema.sql").read_text())
            print("Schema applied")
        password_hash = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode()
        for uid, name, email, role, spec, skills in USERS:
            conn.execute(UPSERT, (uid, name, email, password_hash, role, spec, skills))
        count = conn.execute("select count(*) as n from users").fetchone()["n"]
    print(f"Seeded {len(USERS)} demo users; users table now has {count} rows")


if __name__ == "__main__":
    main()
