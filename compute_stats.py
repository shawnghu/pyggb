import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    args = parser.parse_args()
    hist = {}
    with open(args.file, "r") as f:
        lines = [json.loads(line) for line in f]
    count = 0
    for line in lines:
        if line["correct"]:
            count += 1
    print(count / len(lines))

        # hist[line["difficulty"]] = hist.get(line["difficulty"], 0) + 1
    # print(hist)

if __name__ == "__main__":
    main()