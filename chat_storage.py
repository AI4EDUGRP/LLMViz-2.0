"""
Enhanced Chat & Image Storage Module for LLMViz using Supabase.
Stores complete chat history and generated images in the cloud.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from supabase_client import get_supabase_client


def initialize_storage():
    """No local directories needed with Supabase."""
    pass


def get_chat_history(user_id: str, session_id: str) -> Optional[Dict]:
    """Retrieve full chat history for a session from Supabase."""
    try:
        client = get_supabase_client()
        response = client.table("chats").select("messages").eq("user_id", user_id).eq("session_id", session_id).execute()
        
        if len(response.data) > 0:
            return response.data[0]["messages"]
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        
    return None


def create_chat_session(user_id: str, username: str, session_id: str, dataset_name: str = "") -> Dict:
    """
    Create a new chat session with metadata.
    """
    new_chat = {
        "user_id": user_id,
        "username": username,
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "dataset_name": dataset_name,
        "dataset_summary": {},
        "messages": [],
        "generated_images": [],
        "refinements": [],
        "insights": []
    }
    
    try:
        client = get_supabase_client()
        # insert new chat session, but if (user_id, session_id) already exists, it shouldn't crash if we just return it
        client.table("chats").insert({
            "user_id": user_id, 
            "session_id": session_id, 
            "messages": new_chat
        }).execute()
    except Exception as e:
        print(f"Chat session exists or error: {e}")
        
    return new_chat


def save_chat_message(user_id: str, session_id: str, role: str, content: str, 
                     metadata: Dict = None) -> bool:
    """
    Save a chat message (user or AI) to the session in Supabase.
    """
    metadata = metadata or {}
    try:
        client = get_supabase_client()
        
        # 1. Get current chat data
        response = client.table("chats").select("messages").eq("user_id", user_id).eq("session_id", session_id).execute()
        
        if len(response.data) > 0:
            chat_data = response.data[0]["messages"]
        else:
            chat_data = create_chat_session(user_id, "", session_id)
        
        # 2. Append new message
        message = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata
        }
        
        if "messages" not in chat_data:
            chat_data["messages"] = []
            
        chat_data["messages"].append(message)
        
        # 3. Update database
        client.table("chats").update({"messages": chat_data}).eq("user_id", user_id).eq("session_id", session_id).execute()
        return True
        
    except Exception as e:
        print(f"Error saving chat message: {e}")
        return False


def save_generated_image(user_id: str, session_id: str, image_data: bytes, 
                        chart_type: str, query: str, image_format: str = "png") -> Optional[Dict]:
    """
    Upload a generated chart image to Supabase Storage and update chat metadata.
    Includes compression to save bandwidth and automatic bucket creation.
    """
    try:
        client = get_supabase_client()
        
        # Ensure 'images' bucket exists
        try:
            buckets = client.storage.list_buckets()
            if not any(b.name == 'images' for b in buckets):
                # Create public bucket
                client.storage.create_bucket('images', {'public': True})
        except Exception as e:
            print(f"Bucket check/create error: {e}")
            
        # Compress the image if it's not SVG
        upload_data = image_data
        upload_format = image_format
        
        if image_format.lower() in ['png', 'jpg', 'jpeg']:
            try:
                from PIL import Image
                import io
                
                # Load image from bytes
                img = Image.open(io.BytesIO(image_data))
                
                # Convert to RGB if it's RGBA (JPEG doesn't support alpha)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                # Compress to JPEG
                output_io = io.BytesIO()
                img.save(output_io, format='JPEG', quality=65, optimize=True)
                upload_data = output_io.getvalue()
                upload_format = 'jpeg'
                
                print(f"Compressed image from {len(image_data)} bytes to {len(upload_data)} bytes")
            except Exception as compress_error:
                print(f"Compression failed, using original: {compress_error}")
        
        image_id = str(uuid.uuid4())[:8]
        image_filename = f"{user_id}/{session_id}/chart_{image_id}.{upload_format}"
        
        content_type = f"image/{upload_format}" if upload_format in ["png", "jpeg", "jpg"] else "image/svg+xml"
        
        # Upload
        try:
            res = client.storage.from_("images").upload(
                file=upload_data, 
                path=image_filename,
                file_options={"content-type": content_type}
            )
            # Get public URL
            public_url = client.storage.from_("images").get_public_url(image_filename)
        except Exception as e:
            print(f"Supabase Storage error: {e}. Saving locally.")
            import os
            local_dir = os.path.join("generated_images", user_id, session_id)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, f"chart_{image_id}.{upload_format}")
            with open(local_path, "wb") as f:
                f.write(upload_data)
            public_url = local_path
        
        # Create image metadata
        image_metadata = {
            "id": image_id,
            "filename": image_filename,
            "path": public_url,
            "chart_type": chart_type,
            "user_query": query,
            "generated_at": datetime.now().isoformat()
        }
        
        # Update chat data
        response = client.table("chats").select("messages").eq("user_id", user_id).eq("session_id", session_id).execute()
        if len(response.data) > 0:
            chat_data = response.data[0]["messages"]
        else:
            chat_data = create_chat_session(user_id, "", session_id)
            
        if "generated_images" not in chat_data:
            chat_data["generated_images"] = []
            
        chat_data["generated_images"].append(image_metadata)
        
        client.table("chats").update({"messages": chat_data}).eq("user_id", user_id).eq("session_id", session_id).execute()
        
        return image_metadata
        
    except Exception as e:
        print(f"Error saving generated image to Supabase: {e}")
        return None


def save_chart_refinement(user_id: str, session_id: str, original_query: str, 
                         refinement_query: str, original_image_id: str) -> bool:
    """Save chart refinement data to Supabase."""
    try:
        client = get_supabase_client()
        response = client.table("chats").select("messages").eq("user_id", user_id).eq("session_id", session_id).execute()
        
        if len(response.data) > 0:
            chat_data = response.data[0]["messages"]
            
            refinement = {
                "id": str(uuid.uuid4())[:8],
                "timestamp": datetime.now().isoformat(),
                "original_query": original_query,
                "refinement_query": refinement_query,
                "original_image_id": original_image_id
            }
            
            if "refinements" not in chat_data:
                chat_data["refinements"] = []
                
            chat_data["refinements"].append(refinement)
            
            client.table("chats").update({"messages": chat_data}).eq("user_id", user_id).eq("session_id", session_id).execute()
            return True
            
    except Exception as e:
        print(f"Error saving refinement: {e}")
        
    return False


def save_dataset_summary(user_id: str, session_id: str, summary: Dict) -> bool:
    """Save dataset summary to Supabase."""
    try:
        client = get_supabase_client()
        response = client.table("chats").select("messages").eq("user_id", user_id).eq("session_id", session_id).execute()
        
        if len(response.data) > 0:
            chat_data = response.data[0]["messages"]
            chat_data["dataset_summary"] = summary
            client.table("chats").update({"messages": chat_data}).eq("user_id", user_id).eq("session_id", session_id).execute()
            return True
            
    except Exception as e:
        print(f"Error saving dataset summary: {e}")
    
    return False


def get_session_images(user_id: str, session_id: str) -> List[Dict]:
    """Get all generated images for a session."""
    chat_data = get_chat_history(user_id, session_id)
    if chat_data:
        return chat_data.get("generated_images", [])
    return []


def get_all_user_chats(user_id: str) -> List[Dict]:
    """Get summarized list of user's chats from Supabase."""
    try:
        client = get_supabase_client()
        response = client.table("chats").select("messages").eq("user_id", user_id).execute()
        
        chats = []
        for record in response.data:
            chat = record["messages"]
            # Summarize to match original behavior
            chats.append({
                "session_id": chat.get("session_id"),
                "dataset_name": chat.get("dataset_name", "Unknown Dataset"),
                "created_at": chat.get("created_at"),
                "message_count": len(chat.get("messages", [])),
                "image_count": len(chat.get("generated_images", []))
            })
            
        # Sort by creation date descending
        chats.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return chats
            
    except Exception as e:
        print(f"Error fetching all user chats: {e}")
        return []


def export_chat_to_json(user_id: str, session_id: str, export_path: str) -> bool:
    """Export chat data to a local JSON file (kept for compatibility if user downloads it)."""
    chat_data = get_chat_history(user_id, session_id)
    if not chat_data:
        return False
        
    try:
        with open(export_path, "w") as f:
            json.dump(chat_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting chat: {e}")
        return False


def get_session_statistics(user_id: str, session_id: str) -> Dict:
    """Get statistics about a session."""
    chat_data = get_chat_history(user_id, session_id)
    
    stats = {
        "message_count": 0,
        "user_messages": 0,
        "ai_messages": 0,
        "images_generated": 0,
        "refinements_made": 0,
        "duration_minutes": 0
    }
    
    if not chat_data:
        return stats
        
    messages = chat_data.get("messages", [])
    stats["message_count"] = len(messages)
    stats["user_messages"] = sum(1 for m in messages if m.get("role") == "user")
    stats["ai_messages"] = sum(1 for m in messages if m.get("role") == "assistant")
    stats["images_generated"] = len(chat_data.get("generated_images", []))
    stats["refinements_made"] = len(chat_data.get("refinements", []))
    
    if len(messages) > 1:
        try:
            first_time = datetime.fromisoformat(messages[0]["timestamp"])
            last_time = datetime.fromisoformat(messages[-1]["timestamp"])
            duration = (last_time - first_time).total_seconds() / 60
            stats["duration_minutes"] = round(duration, 1)
        except Exception:
            pass
            
    return stats


def cleanup_images(user_id: str, session_id: str) -> bool:
    """Remove session images from Supabase storage (optional/admin feature)."""
    try:
        client = get_supabase_client()
        # Find all images for this session
        res = client.storage.from_("images").list(f"{user_id}/{session_id}")
        if res:
            files_to_remove = [f"{user_id}/{session_id}/{file['name']}" for file in res]
            if files_to_remove:
                client.storage.from_("images").remove(files_to_remove)
        return True
    except Exception as e:
        print(f"Error cleaning up images: {e}")
        return False
