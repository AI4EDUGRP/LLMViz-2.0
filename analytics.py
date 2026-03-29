"""
Analytics and usage tracking module for LLMViz using Supabase.
Tracks user interactions, queries, and session statistics.
"""

import json
import csv
from datetime import datetime
from typing import Any, Dict, List, Optional
from supabase_client import get_supabase_client


def initialize_analytics():
    """No local directories needed with Supabase."""
    pass


def _get_or_create_session(user_id: str, session_id: str, username: str) -> Dict:
    """Helper to get a session data object from Supabase or create a new one."""
    client = get_supabase_client()
    response = client.table("analytics").select("data").eq("user_id", user_id).eq("session_id", session_id).execute()
    
    if len(response.data) > 0:
        return response.data[0]["data"]
        
    return {
        "user_id": user_id,
        "username": username,
        "session_id": session_id,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "interactions": [],
        "metrics": {
            "queries_made": 0,
            "charts_generated": 0,
            "datasets_uploaded": 0,
            "errors_encountered": 0
        }
    }


def _save_session(user_id: str, session_id: str, data: Dict):
    """Helper to save a session data object to Supabase."""
    client = get_supabase_client()
    
    # Check if exists first
    response = client.table("analytics").select("id").eq("user_id", user_id).eq("session_id", session_id).execute()
    
    if len(response.data) > 0:
        client.table("analytics").update({"data": data}).eq("user_id", user_id).eq("session_id", session_id).execute()
    else:
        client.table("analytics").insert({
            "user_id": user_id,
            "session_id": session_id,
            "data": data
        }).execute()


def log_interaction(user_id: str, username: str, session_id: str, action_type: str, 
                   details: str = "", metadata: Dict = None) -> bool:
    """
    Log a user interaction event.
    """
    metadata = metadata or {}
    
    try:
        data = _get_or_create_session(user_id, session_id, username)
            
        # Create event
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "details": details,
            "metadata": metadata
        }
        
        # Add to interactions
        if "interactions" not in data:
            data["interactions"] = []
        data["interactions"].append(event)
        
        # Update metrics
        if "metrics" not in data:
            data["metrics"] = {
                "queries_made": 0,
                "charts_generated": 0,
                "datasets_uploaded": 0,
                "errors_encountered": 0
            }
            
        if action_type == "query_submit":
            data["metrics"]["queries_made"] += 1
        elif action_type == "chart_generated":
            data["metrics"]["charts_generated"] += 1
        elif action_type == "dataset_upload":
            data["metrics"]["datasets_uploaded"] += 1
        elif action_type == "error":
            data["metrics"]["errors_encountered"] += 1
            
        _save_session(user_id, session_id, data)
        return True
        
    except Exception as e:
        print(f"Error logging interaction: {e}")
        return False


def finalize_session(user_id: str, session_id: str) -> bool:
    """
    Finalize a session, calculating duration.
    """
    try:
        data = _get_or_create_session(user_id, session_id, "Unknown")
        
        # Set end time
        if not data.get("end_time"):
            data["end_time"] = datetime.now().isoformat()
            
            # Calculate duration
            try:
                start = datetime.fromisoformat(data["start_time"])
                end = datetime.fromisoformat(data["end_time"])
                duration_seconds = (end - start).total_seconds()
                data["duration_seconds"] = duration_seconds
                data["duration_minutes"] = round(duration_seconds / 60, 2)
            except Exception:
                pass
                
        _save_session(user_id, session_id, data)
        return True
        
    except Exception as e:
        print(f"Error finalizing session: {e}")
        return False


def get_session_data(user_id: str, session_id: str) -> Dict | None:
    """Get analytics data for a specific session."""
    try:
        client = get_supabase_client()
        response = client.table("analytics").select("data").eq("user_id", user_id).eq("session_id", session_id).execute()
        if len(response.data) > 0:
            return response.data[0]["data"]
    except Exception as e:
        print(f"Error reading session data: {e}")
    return None


def get_all_user_sessions(user_id: str) -> List[Dict]:
    """Get all analytics sessions for a user."""
    sessions = []
    try:
        client = get_supabase_client()
        response = client.table("analytics").select("data").eq("user_id", user_id).execute()
        
        for record in response.data:
            sessions.append(record["data"])
            
        # Sort by start_time descending
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
    except Exception as e:
        print(f"Error getting user sessions: {e}")
        
    return sessions


def get_all_sessions() -> List[Dict]:
    """Get all sessions from all users (admin feature)."""
    sessions = []
    try:
        client = get_supabase_client()
        response = client.table("analytics").select("data").execute()
        
        for record in response.data:
            sessions.append(record["data"])
            
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
    except Exception as e:
        print(f"Error getting all sessions: {e}")
        
    return sessions


def export_sessions_to_csv(filename: str, sessions_data: List[Dict], 
                          include_interactions: bool = False) -> bool:
    """Export session data to a CSV file (useful for admin downloads)."""
    if not sessions_data:
        return False
        
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if not include_interactions:
                fieldnames = ['session_id', 'user_id', 'username', 'start_time', 
                             'end_time', 'duration_minutes', 'queries_made', 
                             'charts_generated', 'datasets_uploaded', 'errors_encountered']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for s in sessions_data:
                    metrics = s.get("metrics", {})
                    writer.writerow({
                        'session_id': s.get('session_id', ''),
                        'user_id': s.get('user_id', ''),
                        'username': s.get('username', ''),
                        'start_time': s.get('start_time', ''),
                        'end_time': s.get('end_time', ''),
                        'duration_minutes': s.get('duration_minutes', 0),
                        'queries_made': metrics.get('queries_made', 0),
                        'charts_generated': metrics.get('charts_generated', 0),
                        'datasets_uploaded': metrics.get('datasets_uploaded', 0),
                        'errors_encountered': metrics.get('errors_encountered', 0)
                    })
            else:
                fieldnames = ['session_id', 'user_id', 'username', 'timestamp', 
                             'action', 'details', 'metadata']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for s in sessions_data:
                    for i in s.get("interactions", []):
                        writer.writerow({
                            'session_id': s.get('session_id', ''),
                            'user_id': s.get('user_id', ''),
                            'username': s.get('username', ''),
                            'timestamp': i.get('timestamp', ''),
                            'action': i.get('action', ''),
                            'details': i.get('details', ''),
                            'metadata': json.dumps(i.get('metadata', {}))
                        })
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def export_sessions_to_json(filename: str, sessions_data: List[Dict], 
                           anonymize: bool = False) -> bool:
    """Export session data to a JSON file (useful for admin downloads)."""
    if not sessions_data:
        return False
        
    try:
        export_data = []
        for s in sessions_data:
            # Create a copy to avoid modifying original
            s_copy = json.loads(json.dumps(s))
            
            if anonymize:
                s_copy['user_id'] = "ANONYMOUS_USER"
                s_copy['username'] = "Anonymous"
                
            export_data.append(s_copy)
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False
