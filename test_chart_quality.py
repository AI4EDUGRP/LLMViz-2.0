"""Failing checks for pie/Unnamed chart quality bugs."""
import re
import pandas as pd

from chart_quality import (
    prepare_dataframe_for_viz,
    demote_bad_composition_charts,
    filter_supported_charts,
    pie_chart_needs_repair,
)


def test_renames_unnamed_columns():
    df = pd.read_csv("MathMatrix_2425_Extraction_Plan.csv")
    cleaned = prepare_dataframe_for_viz(df)
    assert not any(str(c).startswith("Unnamed") for c in cleaned.columns), cleaned.columns.tolist()


def test_demotes_pie_for_long_unique_text():
    df = prepare_dataframe_for_viz(pd.read_csv("MathMatrix_2425_Extraction_Plan.csv"))
    options = ["Pie Chart", "Donut Chart", "Bar/Column Chart"]
    fixed = demote_bad_composition_charts(options, df)
    assert "Pie Chart" not in fixed
    assert "Donut Chart" not in fixed
    assert "Bar/Column Chart" in fixed


def test_detects_bad_pie_code():
    code = """
plt.pie(theme_counts, labels=theme_counts.index, autopct='%1.1f%%')
plt.legend(title='Themes')
"""
    assert pie_chart_needs_repair(code) is True
    assert pie_chart_needs_repair("sns.barplot(data=df, x='a', y='b')") is False


def test_filters_unsupported_seaborn_charts():
    options = ["Treemap", "Sunburst Chart", "Bar/Column Chart", "Pie Chart"]
    fixed = filter_supported_charts(options)
    assert "Treemap" not in fixed
    assert "Sunburst Chart" not in fixed
    assert "Bar/Column Chart" in fixed


if __name__ == "__main__":
    test_renames_unnamed_columns()
    test_demotes_pie_for_long_unique_text()
    test_detects_bad_pie_code()
    test_filters_unsupported_seaborn_charts()
    print("all passed")
