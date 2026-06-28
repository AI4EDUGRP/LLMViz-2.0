import re
import os

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'lida\s*=\s*Manager\(text_gen=llm\([\'"]openai[\'"]\)\)',
    'import tempfile\nimport os\nlida = Manager(text_gen=llm("openai", cache_dir=os.path.join(tempfile.gettempdir(), "lida_cache")))',
    content
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.py successfully.")
