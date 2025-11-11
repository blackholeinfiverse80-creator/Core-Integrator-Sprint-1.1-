import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class ContextMemory:
    """SQLite-based context memory for storing user interactions"""
    
    def __init__(self, db_path: str = "db/context.db"):
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Create table with module column
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    module TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    request_data TEXT NOT NULL,
                    response_data TEXT NOT NULL
                )
            """)
            
            # Check if module column exists (for existing databases)
            cursor = conn.execute("PRAGMA table_info(interactions)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'module' not in columns:
                # Add module column to existing table
                conn.execute("ALTER TABLE interactions ADD COLUMN module TEXT DEFAULT 'unknown'")
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_module_timestamp 
                ON interactions(user_id, module, timestamp DESC)
            """)
    
    def store_interaction(self, user_id: str, request_data: Dict[Any, Any], 
                         response_data: Dict[Any, Any]):
        """Store a request-response interaction"""
        timestamp = datetime.utcnow().isoformat()
        module = request_data.get("module", "unknown")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO interactions (user_id, module, timestamp, request_data, response_data)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, module, timestamp, json.dumps(request_data), json.dumps(response_data)))
            
            # Keep only last 5 entries per user per module
            conn.execute("""
                DELETE FROM interactions 
                WHERE user_id = ? AND module = ? AND id NOT IN (
                    SELECT id FROM interactions 
                    WHERE user_id = ? AND module = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                )
            """, (user_id, module, user_id, module))
    
    def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get full interaction history for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT module, timestamp, request_data, response_data
                FROM interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
            
            return [
                {
                    "module": row[0],
                    "timestamp": row[1],
                    "request": json.loads(row[2]),
                    "response": json.loads(row[3])
                }
                for row in cursor.fetchall()
            ]
    
    def get_context(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get recent context (last N interactions) for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT module, timestamp, request_data, response_data
                FROM interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            return [
                {
                    "module": row[0],
                    "timestamp": row[1],
                    "request": json.loads(row[2]),
                    "response": json.loads(row[3])
                }
                for row in cursor.fetchall()
            ]