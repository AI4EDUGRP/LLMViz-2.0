import json

transcript_path = r'C:\Users\karth\.gemini\antigravity-ide\brain\5c580607-456b-4c1a-8e73-662207d623e4\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        if '"type":"USER_INPUT"' in line:
            data = json.loads(line)
            if '21stdev' in data.get('content', ''):
                with open('user_code.tsx', 'w', encoding='utf-8') as out:
                    out.write(data['content'])
                break
