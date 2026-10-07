import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

# prepare_threshold=None: the Supabase pooler (port 6543) does not support prepared statements.
# autocommit=True: reads don't open a hidden transaction, so `with conn.transaction()` in save.py
# is a real all-or-nothing transaction rather than a savepoint that never commits.
CONN_KWARGS = {"row_factory": dict_row, "prepare_threshold": None, "autocommit": True}

_pool: ConnectionPool | None = None


def connect() -> psycopg.Connection:
    """A standalone connection, for scripts like seed.py."""
    return psycopg.connect(os.environ["DATABASE_URL"], **CONN_KWARGS)


def get_pool() -> ConnectionPool:
    # Opening a connection to a remote DB takes seconds, so the API reuses a small pool
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            os.environ["DATABASE_URL"],
            min_size=1,
            max_size=5,
            kwargs=CONN_KWARGS,
            check=ConnectionPool.check_connection,  # drop connections the pooler closed while idle
            max_idle=300,
            open=True,
        )
    return _pool


def get_db():
    """FastAPI dependency: borrow a pooled connection for the length of the request."""
    with get_pool().connection() as conn:
        yield conn
