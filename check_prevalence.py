# check the prevalence of each command in the dataset
# use this to pseudo-automatically detect if a command is broken but errors are being caught.
# if no instances are reported in ~500 passed generations, then the command is probably broken.

# you can also use this as an early, fast-feedback statistics aggregator for what sorts of constructions are being generated.

from classical_generator import ClassicalGenerator
import geo_types as gt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("timestamp", type=int)
parser.add_argument("--show_all", action="store_true")
parser.add_argument("--show_interesting", action="store_true")
parser.add_argument("--filter_broken", action="store_true")
parser.add_argument("--see_failed", action="store_true") # look in failed dir instead of passed

args = parser.parse_args()

g = ClassicalGenerator()
dict = g._get_commands()

for cmd in dict:
    if 'prove' in cmd or 'measure' in cmd:
        continue # these are special commands, not part of constructions
    # heuristics for not making boring things
    # also minus and power make bad (ambiguous or dependent on calculation precision) problems
    if 'minus' in cmd:
        continue
    if 'sum' in cmd:
        continue
    if 'ratio' in cmd:
        continue
    if 'product' in cmd:
        continue
    if 'power_' in cmd:
        continue

    
    cmd_info = dict[cmd]
    if cmd_info['return_type'] == gt.Boolean:
        continue
    
    # Count occurrences of this command in the dataset
    import os
    import re
    
    # Directory to search
    search_dir = f"passed/{args.timestamp}" if not args.see_failed else f"failed/{args.timestamp}"
    
    # Initialize counter for this command
    cmd_count = 0
    
    # Check if directory exists
    if os.path.exists(search_dir):
        # Iterate through all files in the directory
        for filename in os.listdir(search_dir):
            file_path = os.path.join(search_dir, filename)
            
            # Only process text files
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Count occurrences of the command
                    # Look for the command at the beginning of a line
                    matches = re.findall(r'(?:^|\n)' + re.escape(cmd) + r'\s+:', content)
                    cmd_count += len(matches)
    
    if args.show_all:
        print(f"{cmd}: {cmd_count}")
    elif args.show_interesting:
        if cmd_count == 0 or "polygon" in cmd or "triangle" in cmd:#  or cmd_count == 1:
            print(f"{cmd}: {cmd_count}")
    elif args.filter_broken:
        if cmd_count == 0:#  or cmd_count == 1:
            print(f"{cmd}: {cmd_count}")