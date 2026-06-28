import pandas as pd
from pandas.errors import EmptyDataError


class UploadedDatasetError(ValueError):
    """Raised when an uploaded dataset cannot be used for chart generation."""


def load_dataset_csv(csv_path: str) -> pd.DataFrame:
    """Load a CSV and turn parser failures into user-facing upload errors."""
    try:
        df = pd.read_csv(csv_path)
    except EmptyDataError as exc:
        raise UploadedDatasetError(
            "The uploaded dataset doesn't contain any columns. Please upload a non-empty CSV or a file with a header row."
        ) from exc

    if df.empty or len(df.columns) == 0:
        raise UploadedDatasetError(
            "The uploaded dataset doesn't contain any rows or columns. Please upload a file with tabular data."
        )

    return df


def build_fast_chart_goal(query: str, chart_selected: str) -> str:
    """Build a single LIDA goal with chart and readability constraints."""
    return "\n".join(
        [
            f"User request: {query}",
            f"Use a {chart_selected} chart type.",
            "Do not change to another chart type unless impossible.",
            "Use a large readable figure size, ideally figsize=(12, 7) or larger when labels are long.",
            "Call plt.tight_layout() or use constrained_layout=True so titles, axis labels, tick labels, and legends are not cut off.",
            "Rotate x-axis labels 30 to 45 degrees and right-align them when category labels are long.",
            "If there are many categories, show only the most important/top categories or aggregate the rest as Other.",
            "Move legends outside the plotting area when they overlap data, or place them where they do not obscure marks.",
            "Use readable font sizes for title, labels, ticks, and legend.",
            "Use aesthetically pleasing colors with good contrast.",
            "Keep the chart simple, uncluttered, and easy to understand.",
        ]
    )
