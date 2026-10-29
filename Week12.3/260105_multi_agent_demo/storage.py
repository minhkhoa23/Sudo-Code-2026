from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import secrets
import sqlite3
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Store:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path, check_same_thread=False, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, token_hash TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS threads (id TEXT PRIMARY KEY, user_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS memories (user_id TEXT, key TEXT, value TEXT, updated TEXT, PRIMARY KEY(user_id,key));
        CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, body TEXT);
        CREATE TABLE IF NOT EXISTS outbox (id TEXT PRIMARY KEY, user_id TEXT, recipient TEXT, subject TEXT, body TEXT);
        CREATE TABLE IF NOT EXISTS effects (id TEXT PRIMARY KEY, user_id TEXT, kind TEXT, status TEXT, result TEXT);
        CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, trace_id TEXT, user_id TEXT, run_id TEXT, at TEXT, kind TEXT, data TEXT);
        """)
        self.db.commit()

    def create_user(self):
        user_id, token = uuid4().hex, secrets.token_urlsafe(32)
        with self.db:
            self.db.execute("INSERT INTO users VALUES (?,?)", (user_id, sha256(token.encode()).hexdigest()))
        return {"user_id": user_id, "token": token}

    def authenticate(self, token):
        row = self.db.execute("SELECT id FROM users WHERE token_hash=?", (sha256(token.encode()).hexdigest(),)).fetchone()
        if not row:
            raise PermissionError("Invalid demo session")
        return row["id"]

    def thread(self, user_id, thread_id=None):
        if thread_id:
            row = self.db.execute("SELECT user_id FROM threads WHERE id=?", (thread_id,)).fetchone()
            if not row or row["user_id"] != user_id:
                raise PermissionError("Thread not found for this user")
            return thread_id
        thread_id = uuid4().hex
        with self.db:
            self.db.execute("INSERT INTO threads VALUES (?,?)", (thread_id, user_id))
        return thread_id

    def memories(self, user_id, key=""):
        query = "SELECT key,value,updated FROM memories WHERE user_id=?"
        params = (user_id,)
        if key:
            query += " AND key=?"
            params += (key,)
        return [dict(row) for row in self.db.execute(query + " ORDER BY key LIMIT 20", params)]

    def event(self, state, kind, **data):
        item = {"trace_id": state["trace_id"], "user_id": state["user_id"], "run_id": state["run_id"],
                "at": now(), "kind": kind, "data": data}
        with self.db:
            self.db.execute("INSERT INTO events(trace_id,user_id,run_id,at,kind,data) VALUES (?,?,?,?,?,?)",
                            (item["trace_id"], item["user_id"], item["run_id"], item["at"], kind, canonical(data)))
        return item

    def events(self, user_id, trace_id):
        return [{**dict(row), "data": json.loads(row["data"])} for row in self.db.execute(
            "SELECT seq,trace_id,run_id,at,kind,data FROM events WHERE user_id=? AND trace_id=? ORDER BY seq",
            (user_id, trace_id))]

    def traces(self, user_id):
        return [dict(row) for row in self.db.execute(
            "SELECT trace_id,run_id,MIN(at) AS started,COUNT(*) AS events FROM events WHERE user_id=? GROUP BY trace_id ORDER BY started DESC LIMIT 30", (user_id,))]

    def inventory(self, user_id):
        return {"memories": self.memories(user_id),
                "tickets": [dict(r) for r in self.db.execute("SELECT id,title,body FROM tickets WHERE user_id=?", (user_id,))],
                "outbox": [dict(r) for r in self.db.execute("SELECT id,recipient,subject,body FROM outbox WHERE user_id=?", (user_id,))]}

    def close(self):
        self.db.close()
