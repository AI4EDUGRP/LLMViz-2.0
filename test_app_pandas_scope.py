import ast
import unittest
from pathlib import Path


class AppPandasScopeTest(unittest.TestCase):
    def test_render_analytics_does_not_shadow_global_pandas_import(self):
        app_path = Path(__file__).with_name("app.py")
        tree = ast.parse(app_path.read_text(encoding="utf-8"))
        render_analytics = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "render_analytics"
        )

        pandas_alias_imports = [
            node
            for node in ast.walk(render_analytics)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "pandas" and alias.asname == "pd"
        ]

        self.assertEqual(pandas_alias_imports, [])


if __name__ == "__main__":
    unittest.main()
