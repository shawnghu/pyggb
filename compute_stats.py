import json

hist = {}
with open("natural_language_problems/1744871823_validated_graded_easy_graded_medium.jsonl", "r") as f:
    lines = [json.loads(line) for line in f]
    for line in lines:
        hist[line["difficulty"]] = hist.get(line["difficulty"], 0) + 1
print(hist)