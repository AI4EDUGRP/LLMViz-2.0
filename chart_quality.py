"""Deterministic chart/data quality helpers for Viz Generator."""
from __future__ import annotations

import re
import pandas as pd

_PIE_LIKE = {"pie chart", "donut chart", "sunburst chart"}
# Seaborn/matplotlib executor cannot reliably render these (missing deps / wrong backend)
_UNSUPPORTED_SEABORN = {
    "treemap",
    "sunburst chart",
    "sunburst",
    "word cloud",
    "wordcloud",
    "radar chart",
    "sankey diagram",
    "sankey",
    "chord diagram",
}
_LONG_LABEL_CHARS = 40
_HIGH_CARDINALITY = 8


def filter_supported_charts(options: list[str]) -> list[str]:
    """Remove chart types the seaborn backend cannot execute."""
    kept = []
    for o in options:
        key = o.strip().lower()
        if key in _UNSUPPORTED_SEABORN or key.startswith("treemap"):
            continue
        kept.append(o)
    if not kept:
        kept = ["Bar/Column Chart"]
    return kept


def prepare_dataframe_for_viz(df: pd.DataFrame) -> pd.DataFrame:
    """Rename Unnamed columns and drop empty rows so LIDA gets usable field names."""
    out = df.copy()
    renamed = []
    seen = {}
    for i, col in enumerate(out.columns):
        name = str(col).strip()
        if not name or name.lower().startswith("unnamed"):
            name = "Category" if i == 0 else "Description"
        name = re.sub(r"[^\w]+", "_", name).strip("_") or f"Column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        renamed.append(name)
    out.columns = renamed
    out = out.dropna(how="all")
    return out


def _text_column_is_bad_for_pie(series: pd.Series) -> bool:
    s = series.dropna().astype(str)
    if s.empty:
        return False
    nunique = s.nunique()
    avg_len = s.str.len().mean()
    return nunique > _HIGH_CARDINALITY or avg_len > _LONG_LABEL_CHARS


def demote_bad_composition_charts(options: list[str], df: pd.DataFrame) -> list[str]:
    """Drop pie/donut/unsupported options when they would fail or be unreadable."""
    options = filter_supported_charts(options)
    if df is None or df.empty:
        return options
    bad = any(_text_column_is_bad_for_pie(df[c]) for c in df.columns)
    if not bad:
        return options
    kept = [o for o in options if o.strip().lower() not in _PIE_LIKE]
    if not kept:
        kept = ["Bar/Column Chart"]
    if not any("bar" in o.lower() for o in kept):
        kept = ["Bar/Column Chart"] + kept
    return kept


def pie_chart_needs_repair(code: str) -> bool:
    """True when generated code draws a pie (often unreadable with long labels)."""
    if not code:
        return False
    return bool(re.search(r"\.pie\s*\(", code))


PIE_REPAIR_INSTRUCTIONS = [
    "Replace the pie/donut chart with a horizontal bar chart. Do not call pie at all.",
    "Prefer the column with shorter category labels (keys/themes). Do not use long free-text description fields as categories when a shorter key column exists.",
    "If every category count is 1, you are plotting unique free text — switch to the shorter key/theme column instead.",
    "Use short truncated labels (max ~40 chars with ellipsis) on the y-axis.",
    "Do not draw a legend that repeats the long category names.",
    "Use plt.tight_layout() so labels are fully visible and nothing overlaps.",
    "Title must be short and human-readable; never include Unnamed column names.",
    "Keep one clear quantitative encoding (counts or values) on the x-axis.",
]
