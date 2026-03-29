"""
Authentication and session management for LLMViz using Supabase.
Handles user/admin signup, login, password hashing, and session token management.
"""

import os
import uuid
import hashlib
from datetime import datetime
import bcrypt
from supabase_client import get_supabase_client

# We keep this for backward compatibility if any other module imports it, 
# but auth is now handled by Supabase.
def initialize_data_structure():
    pass

# ==================== Password Hashing ====================
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

# ==================== User Management ====================
def authenticate_user(username: str, pin: str) -> dict | str:
    """
    Authenticate a user or create a new one using a 4-digit PIN.
    Returns: 
    - user dict if successful (login or register)
    - string with error message if failed
    """
    client = get_supabase_client()
    
    if not (isinstance(pin, str) and pin.isdigit() and len(pin) == 4):
        return "PIN must be exactly 4 digits."
        
    response = client.table("app_users").select("*").eq("username", username).eq("is_admin", False).execute()
    
    if len(response.data) > 0:
        user_data = response.data[0]
        if verify_password(pin, user_data["password_hash"]):
            return {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "role": "user",
                "is_new": False
            }
        else:
            return "Invalid PIN for this username."
    
    # Create new user
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    new_user = {
        "user_id": user_id,
        "username": username,
        "password_hash": hash_password(pin),
        "created_at": datetime.now().isoformat(),
        "is_admin": False
    }
    
    client.table("app_users").insert(new_user).execute()
    
    return {
        "user_id": user_id,
        "username": username,
        "role": "user",
        "is_new": True
    }

def create_guest_user() -> dict:
    """
    Create a temporary guest user.
    Returns: user dict
    """
    guest_id = f"guest_{str(uuid.uuid4())[:8]}"
    return {
        "user_id": guest_id,
        "username": f"Guest_{guest_id[-4:]}",
        "role": "guest"
    }

# ==================== Admin Management ====================
def get_master_code() -> str:
    """Get the current master admin signup code from Supabase."""
    try:
        client = get_supabase_client()
        response = client.table("master_codes").select("*").order("created_at", desc=True).limit(1).execute()
        if len(response.data) > 0:
            return response.data[0]["code"]
    except Exception as e:
        print("Error getting master code:", e)
    return os.getenv("ADMIN_MASTER_CODE", "000000")

def set_master_code(new_code: str, admin_id: str) -> bool:
    """
    Set a new master admin code.
    Returns: True if successful
    """
    if not (isinstance(new_code, str) and new_code.isdigit() and len(new_code) == 6):
        return False
    try:
        client = get_supabase_client()
        client.table("master_codes").insert({"code": new_code}).execute()
        return True
    except Exception:
        return False

def register_admin(username: str, password: str, master_code: str) -> dict | None:
    """
    Register a new admin with master code validation.
    Returns: admin dict if successful, None if failed
    """
    current_code = get_master_code()
    if master_code != current_code:
        return None  # Invalid master code
    
    client = get_supabase_client()
    
    # Check if username already exists
    response = client.table("app_users").select("*").eq("username", username).execute()
    if len(response.data) > 0:
        return None  # Username taken
    
    # Create new admin
    admin_id = f"admin_{str(uuid.uuid4())[:8]}"
    new_admin = {
        "user_id": admin_id,
        "username": username,
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "is_admin": True
    }
    
    client.table("app_users").insert(new_admin).execute()
    
    return {
        "admin_id": admin_id,
        "admin_username": username,
        "role": "admin"
    }

def login_admin(username: str, pin: str, master_code: str) -> dict | str:
    """
    Authenticate an admin.
    Returns: admin dict if successful, error message if failed
    """
    current_code = get_master_code()
    if master_code != current_code:
        return "Invalid master code."
    
    client = get_supabase_client()
    response = client.table("app_users").select("*").eq("username", username).eq("is_admin", True).execute()
    
    if len(response.data) > 0:
        admin_data = response.data[0]
        if verify_password(pin, admin_data["password_hash"]):
            return {
                "user_id": admin_data["user_id"],
                "username": admin_data["username"],
                "admin_username": admin_data["username"],
                "role": "admin",
                "is_new": False
            }
        else:
            return "Invalid PIN for this admin account."
    
    return "Admin account not found."

def get_all_admins() -> list:
    """Get list of all registered admins."""
    client = get_supabase_client()
    response = client.table("app_users").select("*").eq("is_admin", True).execute()
    
    return [{"admin_id": a["user_id"], "admin_username": a["username"], 
             "created_at": a["created_at"]} for a in response.data]

# ==================== Session Management ====================
def create_session(user_id: str, username: str, role: str) -> str:
    """
    Create a new session token.
    Returns: session_token
    """
    session_id = f"session_{str(uuid.uuid4())[:8]}"
    session_token = hashlib.sha256(f"{user_id}_{session_id}_{datetime.now().isoformat()}".encode()).hexdigest()
    
    try:
        client = get_supabase_client()
        client.table("sessions").insert({
            "session_id": session_id,
            "user_id": user_id
        }).execute()
    except Exception as e:
        print("Error creating session in DB:", e)
    
    return session_token

def verify_session(session_token: str) -> dict | None:
    """
    Verify if a session token is valid and active.
    Returns: session dict if valid, None otherwise
    """
    # For now, we omit server-side token state caching for stateless deploy
    return None

def end_session(session_token: str) -> bool:
    """
    End a session.
    Returns: True if successful
    """
    return True

def get_all_users() -> list:
    """Get list of all users for admin analytics."""
    client = get_supabase_client()
    response = client.table("app_users").select("*").eq("is_admin", False).execute()
    
    return [{"user_id": u["user_id"], "username": u["username"], 
             "created_at": u["created_at"]} for u in response.data]

def get_all_user_profiles() -> dict:
    """Returns a dict mapping user_id to username from all users and admins."""
    profiles = {}
    
    try:
        client = get_supabase_client()
        response = client.table("app_users").select("user_id, username, is_admin").execute()
        for u in response.data:
            if u["is_admin"]:
                profiles[u["user_id"]] = "Admin: " + u["username"]
            else:
                profiles[u["user_id"]] = u["username"]
    except Exception:
        pass
        
    return profiles
