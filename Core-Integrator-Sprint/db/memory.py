import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class ContextMemory:
    """SQLite-based context memory for storing user interactions"""
    
    def __init__(self, db_path: str = "db/context.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    request_data TEXT NOT NULL,
                    response_data TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                ON interactions(user_id, timestamp DESC)
            """)
    
    def store_interaction(self, user_id: str, request_data: Dict[Any, Any], 
                         response_data: Dict[Any, Any]):
        """Store a request-response interaction"""
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO interactions (user_id, timestamp, request_data, response_data)
                VALUES (?, ?, ?, ?)
            """, (user_id, timestamp, json.dumps(request_data), json.dumps(response_data)))
    
    def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get full interaction history for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, request_data, response_data
                FROM interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
            
            return [
                {
                    "timestamp": row[0],
                    "request": json.loads(row[1]),
                    "response": json.loads(row[2])
                }
                for row in cursor.fetchall()
            ]
    
    def get_context(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get recent context (last N interactions) for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, request_data, response_data
                FROM interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            return [
                {
                    "timestamp": row[0],
                    "request": json.loads(row[1]),
                    "response": json.loads(row[2])
                }
                for row in cursor.fetchall()
            ]