import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "magic_hub",
        url="http://localhost:5173",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "magic_ui/dist")
    _component_func = components.declare_component("magic_hub", path=build_dir)


def render_magic_hero(title: str, subtitle: str, key=None):
    return _component_func(
        componentType="hero",
        title=title,
        subtitle=subtitle,
        key=key,
        default=None,
    )


def render_magic_dashboard(
    key=None,
    is_admin=False,
    username="Guest",
    datasets=None,
    sessions=None,
    visualizations=None,
    stats=None,
    chart_types=None,
    supported_charts=None,
):
    return _component_func(
        componentType="dashboard",
        is_admin=is_admin,
        username=username,
        datasets=datasets or [],
        sessions=sessions or [],
        visualizations=visualizations or [],
        stats=stats or {},
        chart_types=chart_types or [],
        supported_charts=supported_charts or [],
        key=key,
        default=None,
    )


def render_magic_workspace_header(title: str, subtitle: str, icon="generator", key=None):
    return _component_func(
        componentType="workspace",
        title=title,
        subtitle=subtitle,
        icon=icon,
        key=key,
        default=None,
    )


def render_magic_empty_canvas(title=None, description=None, key=None):
    return _component_func(
        componentType="empty_canvas",
        title=title,
        description=description,
        key=key,
        default=None,
    )


def render_magic_evaluator_header(title=None, subtitle=None, key=None):
    return _component_func(
        componentType="evaluator",
        title=title,
        subtitle=subtitle,
        key=key,
        default=None,
    )


def render_magic_analytics(
    total_users=0,
    total_visualizations=0,
    total_datasets=0,
    total_interactions=0,
    avg_session_duration="—",
    top_chart_types=None,
    top_actions=None,
    key=None,
):
    return _component_func(
        componentType="analytics",
        total_users=total_users,
        total_visualizations=total_visualizations,
        total_datasets=total_datasets,
        total_interactions=total_interactions,
        avg_session_duration=avg_session_duration,
        top_chart_types=top_chart_types or [],
        top_actions=top_actions or [],
        key=key,
        default=None,
    )


def render_magic_page_nav(active="home", is_admin=False, key=None):
    return _component_func(
        componentType="page_nav",
        active=active,
        is_admin=is_admin,
        key=key,
        default=None,
    )


def render_magic_feedback(feedback_text: str, key=None):
    return _component_func(
        componentType="feedback",
        feedback_text=feedback_text,
        key=key,
        default=None,
    )


def render_magic_auth(key=None, error_message=None):
    return _component_func(
        componentType="auth",
        error_message=error_message,
        key=key,
        default=None,
    )
