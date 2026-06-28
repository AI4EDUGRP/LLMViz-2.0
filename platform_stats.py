"""
Platform-wide usage statistics for the public home dashboard.
Aggregates Supabase (primary) and local SQLite (supplement/fallback).
"""

from typing import Dict

from analytics import get_all_sessions
from supabase_client import get_supabase_client


def get_platform_dashboard_stats() -> Dict:
    """All-time platform totals for the public home dashboard."""
    result = {
        "datasets": 0,
        "visualizations": 0,
        "chat_queries": 0,
        "users": 0,
        "interactions": 0,
        "top_chart_types": [],
    }

    # --- Supabase analytics + chats ---
    try:
        from auth import get_all_user_profiles

        user_profiles = get_all_user_profiles()
        result["users"] = len(user_profiles)

        datasets = 0
        visualizations = 0
        interactions = 0
        chat_queries = 0
        chart_counts: Dict[str, int] = {}

        for session in get_all_sessions():
            session_interactions = session.get("interactions", [])
            interactions += len(session_interactions)

            for event in session_interactions:
                action = event.get("action", "")
                if action in ("dataset_upload", "file_upload"):
                    datasets += 1
                elif action in (
                    "chart_generated",
                    "ai_query",
                    "chart_refinement",
                    "chart_evaluation",
                ):
                    visualizations += 1
                if action in ("query_submit", "ai_query"):
                    chat_queries += 1

        client = get_supabase_client()
        chats_response = client.table("chats").select("messages").execute()
        user_messages = 0
        chat_images = 0

        for record in chats_response.data:
            chat = record.get("messages") or {}
            for message in chat.get("messages", []):
                if message.get("role") == "user":
                    user_messages += 1
            for image in chat.get("generated_images", []):
                chat_images += 1
                chart_type = image.get("chart_type", "Unknown")
                chart_counts[chart_type] = chart_counts.get(chart_type, 0) + 1

        result["datasets"] = datasets
        result["visualizations"] = max(visualizations, chat_images)
        result["chat_queries"] = max(chat_queries, user_messages)
        result["interactions"] = interactions
        result["top_chart_types"] = [
            {"viz_type": chart_type, "count": count}
            for chart_type, count in sorted(
                chart_counts.items(), key=lambda item: item[1], reverse=True
            )[:8]
        ]
    except Exception as e:
        print(f"Supabase platform stats unavailable: {e}")

    # --- Local SQLite (supplement when Supabase is partial or unavailable) ---
    try:
        from database import get_db

        local = get_db().get_dashboard_stats()
        result["datasets"] = max(result["datasets"], local.get("total_datasets", 0))
        result["visualizations"] = max(
            result["visualizations"], local.get("total_visualizations", 0)
        )
        result["chat_queries"] = max(
            result["chat_queries"], local.get("total_conversations", 0)
        )
        result["users"] = max(result["users"], local.get("total_users", 0))
        result["interactions"] = max(
            result["interactions"], local.get("total_interactions", 0)
        )

        if not result["top_chart_types"] and local.get("top_chart_types"):
            result["top_chart_types"] = [
                {"viz_type": row["viz_type"], "count": row["count"]}
                for row in local["top_chart_types"]
            ]
    except Exception as e:
        print(f"SQLite platform stats unavailable: {e}")

    return result
