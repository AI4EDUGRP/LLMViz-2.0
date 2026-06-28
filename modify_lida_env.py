import re
import os

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

old_string = 'import tempfile\nimport os\nlida = Manager(text_gen=llm("openai", cache_dir=os.path.join(tempfile.gettempdir(), "lida_cache")))'
new_string = 'import tempfile\nimport os\nos.environ["LOCALAPPDATA"] = os.path.join(tempfile.gettempdir(), "lida_appdata")\nlida = Manager(text_gen=llm("openai"))'

if old_string in content:
    content = content.replace(old_string, new_string)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated app.py successfully with LOCALAPPDATA workaround.")
else:
    print("Could not find the target string to replace.")
