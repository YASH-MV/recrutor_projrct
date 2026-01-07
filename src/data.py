import sqlite3
from pathlib import Path
import json
import uuid


DB_PATH = Path("database") / "recruitiq.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            interviewer TEXT,
            date TEXT,
            notes TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            name TEXT,
            email TEXT,
            phone TEXT,
            position TEXT,
            experience_years INTEGER,
            notes TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT,
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    conn.close()


def create_session(name, interviewer=None, date=None, notes=None):
    sid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO sessions (id, name, interviewer, date, notes) VALUES (?, ?, ?, ?, ?)",
        (sid, name, interviewer, date, notes),
    )
    conn.commit()
    conn.close()
    return sid


def list_sessions():
    conn = get_conn()
    cur = conn.execute("SELECT * FROM sessions ORDER BY date DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def add_candidate(session_id, name, email=None, phone=None, position=None, experience_years=None, notes=None):
    cid = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO candidates (id, session_id, name, email, phone, position, experience_years, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cid, session_id, name, email, phone, position, experience_years, notes),
    )
    conn.commit()
    conn.close()
    return cid


def list_candidates(session_id):
    conn = get_conn()
    cur = conn.execute("SELECT * FROM candidates WHERE session_id = ?", (session_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def add_score(candidate_id, metric, value):
    conn = get_conn()
    conn.execute("INSERT INTO scores (candidate_id, metric, value) VALUES (?, ?, ?)", (candidate_id, metric, value))
    conn.commit()
    conn.close()


def get_scores_for_candidate(candidate_id):
    conn = get_conn()
    cur = conn.execute("SELECT metric, value FROM scores WHERE candidate_id = ?", (candidate_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_aggregate_scores(session_id):
    conn = get_conn()
    cur = conn.execute(
        """
        SELECT c.id as candidate_id, c.name, s.metric, AVG(s.value) as avg_value
        FROM candidates c
        LEFT JOIN scores s ON c.id = s.candidate_id
        WHERE c.session_id = ?
        GROUP BY c.id, s.metric
        """,
        (session_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_candidate_scores(candidate_id):
    """Delete all scores for a candidate (used when updating scores)"""
    conn = get_conn()
    conn.execute("DELETE FROM scores WHERE candidate_id = ?", (candidate_id,))
    conn.commit()
    conn.close()


def update_candidate_notes(candidate_id, notes):
    """Update candidate notes"""
    conn = get_conn()
    conn.execute("UPDATE candidates SET notes = ? WHERE id = ?", (notes, candidate_id))
    conn.commit()
    conn.close()


def get_candidate_by_id(candidate_id):
    """Get a single candidate by ID"""
    conn = get_conn()
    cur = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_scores_for_session(session_id):
    """Get all scores for all candidates in a session"""
    conn = get_conn()
    cur = conn.execute(
        """
        SELECT c.id as candidate_id, c.name, s.metric, s.value
        FROM candidates c
        JOIN scores s ON c.id = s.candidate_id
        WHERE c.session_id = ?
        ORDER BY c.name, s.metric
        """,
        (session_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows