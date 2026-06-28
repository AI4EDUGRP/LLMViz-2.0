import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os

DB_PATH = "visualstats.db"


class DatabaseManager:
    """Handles all database operations for VisualStats platform."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize the database with all required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                session_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_type TEXT,
                last_active TIMESTAMP,
                anonymous_name TEXT
            )
        """)

        # Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                action_details TEXT,
                page_section TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # AI Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT,
                ai_response TEXT,
                visualization_generated BOOLEAN DEFAULT 0,
                chart_type TEXT,
                model_used TEXT DEFAULT 'gpt-4o',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dataset_name TEXT,
                file_type TEXT,
                file_size_bytes INTEGER,
                num_rows INTEGER,
                num_columns INTEGER,
                column_names TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Visualizations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visualizations (
                viz_id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                viz_type TEXT NOT NULL,
                columns_used TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT,
                validation_status TEXT,
                feedback TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Clickstream table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clickstream (
                click_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                element_type TEXT,
                element_name TEXT,
                page_url TEXT,
                session_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Images / Evaluator images tracking
        # Try to add image_path and source_type to visualizations to avoid migration scripts
        try:
            cursor.execute(
                "ALTER TABLE visualizations ADD COLUMN image_path TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute(
                "ALTER TABLE visualizations ADD COLUMN source_type TEXT DEFAULT 'generated'")
        except sqlite3.OperationalError:
            pass

        # Session table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                datasets_uploaded INTEGER,
                visualizations_created INTEGER,
                queries_made INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_user(self, device_type: str = None) -> str:
        """Create a new user and return user_id."""
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        anonymous_name = self._generate_anonymous_name()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, session_id, device_type, last_active, anonymous_name)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_id, device_type, datetime.now(), anonymous_name))
        conn.commit()
        conn.close()

        return user_id

    def _generate_anonymous_name(self) -> str:
        """Generate a random anonymous name for privacy."""
        adjectives = ["curious", "smart", "brave",
            "swift", "keen", "bright", "clever"]
        animals = ["otter", "squirrel", "fox",
            "eagle", "dolphin", "panda", "wolf"]
        import random
        return f"{random.choice(adjectives)}_{random.choice(animals)}"

    def log_interaction(self, user_id: str, action_type: str,
                       action_details: Dict = None, page_section: str = None) -> str:
        """Log a user interaction."""
        interaction_id = str(uuid.uuid4())

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interactions
            (interaction_id, user_id, action_type, action_details, page_section)
            VALUES (?, ?, ?, ?, ?)
        """, (interaction_id, user_id, action_type, json.dumps(action_details) if action_details else None, page_section))
        conn.commit()
        conn.close()

        return interaction_id

    def log_ai_conversation(self, user_id: str, user_query: str,
                           ai_response: str, visualization_generated: bool = False,
                           chart_type: str = None) -> str:
        """Log an AI conversation."""
        conversation_id = str(uuid.uuid4())

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_conversations
            (conversation_id, user_id, user_query,
             ai_response, visualization_generated, chart_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (conversation_id, user_id, user_query, ai_response, visualization_generated, chart_type))
        conn.commit()
        conn.close()

        return conversation_id

    def log_dataset_upload(self, user_id: str, dataset_name: str,
                          file_type: str, file_size: int, num_rows: int,
                          num_columns: int, column_names: List[str]) -> str:
        """Log a dataset upload."""
        dataset_id = str(uuid.uuid4())

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO datasets
            (dataset_id, user_id, dataset_name, file_type, file_size_bytes,
             num_rows, num_columns, column_names)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dataset_id, user_id, dataset_name, file_type, file_size,
              num_rows, num_columns, json.dumps(column_names)))
        conn.commit()
        conn.close()

        return dataset_id


    def log_visualization(self, user_id: str, dataset_id: str, viz_type: str,
                         columns_used: List[str], user_query: str = None,
                         validation_status: str = None, image_path: str = None,
                         source_type: str = 'generated') -> str:
        """Log a generated visualization."""
        viz_id = str(uuid.uuid4())

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO visualizations
            (viz_id, dataset_id, user_id, viz_type, columns_used,
             user_query, validation_status, image_path, source_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (viz_id, dataset_id, user_id, viz_type, json.dumps(columns_used), user_query, validation_status, image_path, source_type))
        conn.commit()
        conn.close()

        return viz_id

    def log_click(self, user_id: str, element_type: str, element_name: str, session_id: str = None, page_url: str = None) -> str:
        """Log a clickstream event."""
        click_id = str(uuid.uuid4())
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clickstream 
            (click_id, user_id, element_type, element_name, session_id, page_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (click_id, user_id, element_type, element_name, session_id, page_url))
        conn.commit()
        conn.close()
        
        return click_id
    
    def create_session(self, user_id: str) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id)
            VALUES (?, ?)
        """, (session_id, user_id))
        conn.commit()
        conn.close()
        
        return session_id
    
    def end_session(self, session_id: str, datasets_uploaded: int = 0,
                   visualizations_created: int = 0, queries_made: int = 0):
        """End a session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate duration
        cursor.execute("SELECT start_time FROM sessions WHERE session_id = ?", (session_id,))
        result = cursor.fetchone()
        if result:
            start_time = datetime.fromisoformat(result['start_time'])
            duration = (datetime.now() - start_time).total_seconds()
            
            cursor.execute("""
                UPDATE sessions 
                SET end_time = ?, duration_seconds = ?,
                    datasets_uploaded = ?, visualizations_created = ?, queries_made = ?
                WHERE session_id = ?
            """, (datetime.now(), int(duration), datasets_uploaded, 
                  visualizations_created, queries_made, session_id))
        
        conn.commit()
        conn.close()
    
    def get_user_interactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get recent interactions for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM interactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
        
    def get_all_active_users(self) -> List[str]:
        """Get list of active user_ids from interactions and conversations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT user_id FROM interactions
            UNION
            SELECT DISTINCT user_id FROM ai_conversations
        """)
        
        results = [row['user_id'] for row in cursor.fetchall() if row['user_id']]
        conn.close()
        return results

    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ai_conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_user_visualizations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get tracked visualization images for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # We try to select source_type and image_path, but handle old schema just in case
        try:
            cursor.execute("""
                SELECT viz_id, viz_type, user_query, generated_at, validation_status, image_path, source_type 
                FROM visualizations 
                WHERE user_id = ? 
                ORDER BY generated_at DESC 
                LIMIT ?
            """, (user_id, limit))
        except sqlite3.OperationalError:
            cursor.execute("""
                SELECT viz_id, viz_type, user_query, generated_at, validation_status 
                FROM visualizations 
                WHERE user_id = ? 
                ORDER BY generated_at DESC 
                LIMIT ?
            """, (user_id, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_dashboard_stats(self) -> Dict:
        """Get platform statistics for dashboard."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        stats['total_users'] = cursor.fetchone()['count']
        
        # Total interactions
        cursor.execute("SELECT COUNT(*) as count FROM interactions")
        stats['total_interactions'] = cursor.fetchone()['count']
        
        # Total visualizations
        cursor.execute("SELECT COUNT(*) as count FROM visualizations")
        stats['total_visualizations'] = cursor.fetchone()['count']
        
        # Total datasets uploaded
        cursor.execute("SELECT COUNT(*) as count FROM datasets")
        stats['total_datasets'] = cursor.fetchone()['count']
        
        # Most used chart types
        cursor.execute("""
            SELECT viz_type, COUNT(*) as count FROM visualizations 
            GROUP BY viz_type 
            ORDER BY count DESC 
            LIMIT 5
        """)
        stats['top_chart_types'] = [dict(row) for row in cursor.fetchall()]
        
        # Average session duration
        cursor.execute("""
            SELECT AVG(duration_seconds) as avg_duration FROM sessions 
            WHERE duration_seconds IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_session_duration'] = result['avg_duration'] if result['avg_duration'] else 0
        
        # Most common actions
        cursor.execute("""
            SELECT action_type, COUNT(*) as count FROM interactions 
            GROUP BY action_type 
            ORDER BY count DESC 
            LIMIT 5
        """)
        stats['top_actions'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return stats


# Global DB instance
db = None

def get_db() -> DatabaseManager:
    """Get or create the global database instance."""
    global db
    if db is None:
        db = DatabaseManager()
    return db
