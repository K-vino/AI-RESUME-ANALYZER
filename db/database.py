# db/database.py

import sqlite3
from datetime import datetime
import json

class ResumeMatchDB:
    def __init__(self, db_path="resume_analyzer.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Candidates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    resume_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Job Descriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Matches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    job_id INTEGER,
                    match_score REAL,
                    skills_match REAL,
                    experience_match REAL,
                    education_match REAL,
                    certifications_match REAL,
                    summary TEXT,
                    is_shortlisted BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                    FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
                )
            ''')
            
            # Interviews table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER,
                    job_id INTEGER,
                    scheduled_date TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    interviewer TEXT,
                    meeting_link TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                    FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
                )
            ''')
            
            conn.commit()

    def insert_candidate(self, name, email, resume_path):
        """Insert a new candidate"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO candidates (name, email, resume_path) VALUES (?, ?, ?)",
                (name, email, resume_path)
            )
            return cursor.lastrowid

    def insert_job_description(self, title, description):
        """Insert a new job description"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO job_descriptions (title, description) VALUES (?, ?)",
                (title, description)
            )
            return cursor.lastrowid

    def insert_match_result(self, candidate_id, job_id, match_data):
        """Insert match results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO matches (
                    candidate_id, job_id, match_score, skills_match,
                    experience_match, education_match, certifications_match,
                    summary, is_shortlisted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate_id, job_id,
                match_data['match_score'],
                match_data['skills_match'],
                match_data['experience_match'],
                match_data['education_match'],
                match_data['certifications_match'],
                match_data['summary'],
                match_data['is_shortlisted']
            ))
            return cursor.lastrowid

    def schedule_interview(self, candidate_id, job_id, scheduled_date, interviewer, meeting_link=None, notes=None):
        """Schedule an interview"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interviews (
                    candidate_id, job_id, scheduled_date,
                    interviewer, meeting_link, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (candidate_id, job_id, scheduled_date, interviewer, meeting_link, notes))
            return cursor.lastrowid

    def get_candidate_matches(self, candidate_id):
        """Get all matches for a candidate"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.*, j.title as job_title, j.description as job_description
                FROM matches m
                JOIN job_descriptions j ON m.job_id = j.id
                WHERE m.candidate_id = ?
                ORDER BY m.match_score DESC
            ''', (candidate_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_scheduled_interviews(self, status=None):
        """Get all scheduled interviews, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # This makes the cursor return dictionaries
            cursor = conn.cursor()
            if status:
                cursor.execute('''
                    SELECT i.*, c.name as candidate_name, c.email as candidate_email,
                           j.title as job_title
                    FROM interviews i
                    JOIN candidates c ON i.candidate_id = c.id
                    JOIN job_descriptions j ON i.job_id = j.id
                    WHERE i.status = ?
                    ORDER BY i.scheduled_date
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT i.*, c.name as candidate_name, c.email as candidate_email,
                           j.title as job_title
                    FROM interviews i
                    JOIN candidates c ON i.candidate_id = c.id
                    JOIN job_descriptions j ON i.job_id = j.id
                    ORDER BY i.scheduled_date
                ''')
            return [dict(row) for row in cursor.fetchall()]

    def update_interview_status(self, interview_id, status, notes=None):
        """Update interview status and notes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if notes:
                cursor.execute('''
                    UPDATE interviews
                    SET status = ?, notes = ?
                    WHERE id = ?
                ''', (status, notes, interview_id))
            else:
                cursor.execute('''
                    UPDATE interviews
                    SET status = ?
                    WHERE id = ?
                ''', (status, interview_id))
            conn.commit()

    def close(self):
        """Close database connection"""
        pass  # SQLite connections are automatically closed
