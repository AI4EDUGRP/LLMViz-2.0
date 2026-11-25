"""
Analytics and usage tracking module for LLMViz using Supabase.
Tracks user interactions, queries, and session statistics.
"""

import csv
import io
import json
import re
import zipfile
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
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


def _parse_day(ts: str | None) -> date | None:
    if not ts or not isinstance(ts, str):
        return None
    raw = ts.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw).date()
    except Exception:
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").date()
        except Exception:
            return None


def _safe_folder_name(name: str) -> str:
    cleaned = re.sub(r"[^\w.\-]+", "_", (name or "unknown").strip())
    return (cleaned[:80] or "unknown").strip("_")


def _session_in_date_range(session: Dict, start: date, end: date) -> bool:
    for key in ("start_time", "end_time"):
        d = _parse_day(session.get(key))
        if d and start <= d <= end:
            return True
    for event in session.get("interactions", []) or []:
        d = _parse_day(event.get("timestamp"))
        if d and start <= d <= end:
            return True
    return False


def _chat_in_date_range(chat_data: Dict, start: date, end: date) -> bool:
    d = _parse_day(chat_data.get("created_at"))
    if d and start <= d <= end:
        return True
    for msg in chat_data.get("messages", []) or []:
        d = _parse_day(msg.get("timestamp"))
        if d and start <= d <= end:
            return True
    for img in chat_data.get("generated_images", []) or []:
        d = _parse_day(img.get("generated_at") or img.get("created_at"))
        if d and start <= d <= end:
            return True
    return False


def _download_image_bytes(client, image_meta: Dict) -> Tuple[str, bytes] | None:
    """Fetch chart image bytes from Supabase Storage or public URL."""
    filename = image_meta.get("filename") or ""
    path = image_meta.get("path") or ""
    image_id = image_meta.get("id") or "chart"
    ext = "jpeg"
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1]
    elif path.lower().endswith(".png"):
        ext = "png"

    # Prefer storage path
    if filename and not str(filename).startswith("http"):
        try:
            data = client.storage.from_("images").download(filename)
            if data:
                return f"chart_{image_id}.{ext}", data
        except Exception as e:
            print(f"Storage download failed for {filename}: {e}")

    url = path if str(path).startswith("http") else None
    if url:
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
                if data:
                    return f"chart_{image_id}.{ext}", data
        except Exception as e:
            print(f"URL download failed for {url}: {e}")
    return None


def build_dated_student_export_zip(start: date, end: date) -> Tuple[bytes, Dict[str, int]]:
    """
    Build a ZIP of student activity for [start, end] (inclusive).

    Layout:
      summary.csv
      <StudentName>/
        overview.csv
        session_<id>/
          analytics.json
          chat_history.json
          images/...
    """
    if end < start:
        start, end = end, start

    from chat_storage import get_chat_history
    from auth import get_all_user_profiles

    client = get_supabase_client()
    profiles = get_all_user_profiles()
    all_sessions = get_all_sessions()

    # user_id -> list of analytics sessions in range
    sessions_by_user: Dict[str, List[Dict]] = {}
    for s in all_sessions:
        if not _session_in_date_range(s, start, end):
            continue
        uid = s.get("user_id") or "unknown"
        sessions_by_user.setdefault(uid, []).append(s)

    # Also pull chats in range (covers users with chats but thin analytics)
    chats_by_user: Dict[str, List[Dict]] = {}
    try:
        chat_rows = client.table("chats").select("user_id, session_id, messages").execute()
        for row in chat_rows.data or []:
            chat_data = row.get("messages") or {}
            if not isinstance(chat_data, dict):
                continue
            if not _chat_in_date_range(chat_data, start, end):
                continue
            uid = row.get("user_id") or chat_data.get("user_id") or "unknown"
            chat_data.setdefault("session_id", row.get("session_id"))
            chat_data.setdefault("user_id", uid)
            chats_by_user.setdefault(uid, []).append(chat_data)
    except Exception as e:
        print(f"Error loading chats for export: {e}")

    user_ids = sorted(set(sessions_by_user) | set(chats_by_user))
    buf = io.BytesIO()
    summary_rows = []
    image_count = 0

    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for uid in user_ids:
            display = profiles.get(uid) or (sessions_by_user.get(uid) or [{}])[0].get("username")
            if not display and chats_by_user.get(uid):
                display = chats_by_user[uid][0].get("username")
            display = display or uid
            folder = _safe_folder_name(str(display))

            user_sessions = sessions_by_user.get(uid, [])
            user_chats = chats_by_user.get(uid, [])

            # overview.csv per student
            overview = io.StringIO()
            ow = csv.DictWriter(
                overview,
                fieldnames=[
                    "user_id", "username", "session_id", "start_time", "end_time",
                    "duration_minutes", "queries_made", "charts_generated",
                    "datasets_uploaded", "interaction_count",
                ],
            )
            ow.writeheader()
            for s in user_sessions:
                metrics = s.get("metrics") or {}
                ow.writerow({
                    "user_id": uid,
                    "username": display,
                    "session_id": s.get("session_id", ""),
                    "start_time": s.get("start_time", ""),
                    "end_time": s.get("end_time", ""),
                    "duration_minutes": s.get("duration_minutes", 0),
                    "queries_made": metrics.get("queries_made", 0),
                    "charts_generated": metrics.get("charts_generated", 0),
                    "datasets_uploaded": metrics.get("datasets_uploaded", 0),
                    "interaction_count": len(s.get("interactions") or []),
                })
            zf.writestr(f"{folder}/overview.csv", overview.getvalue())

            # Index chats by session
            chat_by_sid = {c.get("session_id"): c for c in user_chats if c.get("session_id")}
            session_ids = set(s.get("session_id") for s in user_sessions if s.get("session_id"))
            session_ids |= set(chat_by_sid.keys())

            student_images = 0
            for sid in sorted(session_ids):
                if not sid:
                    continue
                sess_folder = f"{folder}/session_{_safe_folder_name(str(sid))}"
                analytics_sess = next((s for s in user_sessions if s.get("session_id") == sid), None)
                if analytics_sess:
                    zf.writestr(
                        f"{sess_folder}/analytics.json",
                        json.dumps(analytics_sess, indent=2),
                    )
                chat_data = chat_by_sid.get(sid) or get_chat_history(uid, sid)
                if chat_data:
                    zf.writestr(
                        f"{sess_folder}/chat_history.json",
                        json.dumps(chat_data, indent=2),
                    )
                    for img_meta in chat_data.get("generated_images") or []:
                        fetched = _download_image_bytes(client, img_meta)
                        if not fetched:
                            continue
                        fname, data = fetched
                        zf.writestr(f"{sess_folder}/images/{fname}", data)
                        student_images += 1
                        image_count += 1

            summary_rows.append({
                "username": display,
                "user_id": uid,
                "sessions": len(session_ids),
                "analytics_sessions": len(user_sessions),
                "chat_sessions": len(user_chats),
                "images": student_images,
            })

        # Root summary
        summary_io = io.StringIO()
        sw = csv.DictWriter(
            summary_io,
            fieldnames=["username", "user_id", "sessions", "analytics_sessions", "chat_sessions", "images"],
        )
        sw.writeheader()
        for row in summary_rows:
            sw.writerow(row)
        zf.writestr("summary.csv", summary_io.getvalue())

        # Flat interactions CSV for quick spreadsheet use
        flat = io.StringIO()
        fw = csv.DictWriter(
            flat,
            fieldnames=["username", "user_id", "session_id", "timestamp", "action", "details"],
        )
        fw.writeheader()
        for uid in user_ids:
            display = profiles.get(uid) or uid
            for s in sessions_by_user.get(uid, []):
                for i in s.get("interactions") or []:
                    fw.writerow({
                        "username": display,
                        "user_id": uid,
                        "session_id": s.get("session_id", ""),
                        "timestamp": i.get("timestamp", ""),
                        "action": i.get("action", ""),
                        "details": json.dumps(i.get("details", "")),
                    })
        zf.writestr("all_interactions.csv", flat.getvalue())

    stats = {
        "students": len(user_ids),
        "sessions": sum(len(v) for v in sessions_by_user.values()),
        "images": image_count,
    }
    return buf.getvalue(), stats
