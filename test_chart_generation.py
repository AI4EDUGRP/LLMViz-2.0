import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from chart_generation import UploadedDatasetError, build_fast_chart_goal, load_dataset_csv


class ChartGenerationGoalTest(unittest.TestCase):
    def test_build_fast_chart_goal_includes_chart_type_and_readability_guidance(self):
        goal = build_fast_chart_goal(
            query="How does frequency vary over time?",
            chart_selected="Line Chart",
        )

        self.assertIn("How does frequency vary over time?", goal)
        self.assertIn("Line Chart", goal)
        self.assertIn("Do not change to another chart type unless impossible", goal)
        self.assertIn("Rotate x-axis labels", goal)
        self.assertIn("Keep the chart simple", goal)


class DatasetCsvLoaderTest(unittest.TestCase):
    def test_empty_csv_raises_user_friendly_upload_error(self):
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "empty.csv"
            csv_path.write_text("", encoding="utf-8")

            with self.assertRaises(UploadedDatasetError) as ctx:
                load_dataset_csv(str(csv_path))

        self.assertIn("doesn't contain any columns", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
