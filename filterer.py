import json
from tqdm import tqdm
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--output_file", type=str)
    args = parser.parse_args()
    lines = [json.loads(line) for line in open(args.input_file, "r")]
    if not args.output_file:
        args.output_file = args.input_file.replace(".jsonl", "_filtered.jsonl")
    with open(args.output_file, "w") as f:
        for line in tqdm(lines, desc="Processing questions"):
            if line["correct"]:
                f.write(json.dumps(line) + "\n")

if __name__ == "__main__":
    main()