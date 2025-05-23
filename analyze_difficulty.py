import argparse
import json
import matplotlib.pyplot as plt
import os
import numpy as np
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        first_time = True
        for line in f:
            data = json.loads(line)
            if first_time:
                first_time = False
                stats = {k: [] for k in data["stats"]}
            prop_correct = data["qwen_correct_trials"] / data["qwen_trials"]
            for k in data["stats"]:
                stats[k].append((data["stats"][k], prop_correct))

    basename = os.path.basename(args.input_file).split("_")[0]
    os.makedirs(f"plots/{basename}", exist_ok=True)
    for k in stats:
        # Group data into difficulty categories
        categories = {'easy': [], 'medium': [], 'hard': []}
        for value, correct_rate in stats[k]:
            if correct_rate > 0.8:
                categories['easy'].append(value)
            elif correct_rate >= 0.2:
                categories['medium'].append(value)
            else:
                categories['hard'].append(value)
        
        # Count occurrences of each input value in each category
        all_values = [x[0] for x in stats[k]]
        unique_values = sorted(set(all_values))
        
        easy_counts = [categories['easy'].count(val) for val in unique_values]
        medium_counts = [categories['medium'].count(val) for val in unique_values]
        hard_counts = [categories['hard'].count(val) for val in unique_values]
        '''
        # Create the multi-bar chart
        width = 0.25
        x = np.arange(len(unique_values))

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width, easy_counts, width, label='Easy (>0.8)')
        ax.bar(x, medium_counts, width, label='Medium (0.2-0.8)')
        ax.bar(x + width, hard_counts, width, label='Hard (<0.2)')
        
        ax.set_xlabel(f'Value of {k}')
        ax.set_ylabel('Count')
        ax.set_title(f'Distribution of {k} by Difficulty')
        ax.set_xticks(x)
        ax.set_xticklabels(unique_values)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f"plots/{basename}/{k}_difficulty_distribution.png")
        plt.close()
        '''
        plt.scatter(np.array(stats[k])[:, 0], np.array(stats[k])[:, 1])
        plt.savefig(f"plots/{basename}/{k}.png")
        plt.close()
        

if __name__ == "__main__":
    main()