# simple script for output.jsonl to compute statistics

import json

with open("output.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

print(f"Total correct: {sum(item['correct'] for item in data)}")
print(f"Total questions: {len(data)}")
