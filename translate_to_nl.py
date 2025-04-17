import os
import argparse
import glob
from typing import List, Optional, Dict
from pathlib import Path
import openai
import dotenv
import time
import hashlib
from openai import OpenAI
import time
import json
global_timestamp = str(int(time.time()))

def create_context():
    context = "Here are some relevant files:\n\n"
    
    for filename in ["commands.py", "geo_types.py", "measure_test.py", "random_constr.py"]:
        with open(filename, 'r') as f:
            commands_content = f.read()
        short_filename = os.path.basename(filename)
        context += f"# {short_filename}:\n```\n"
        context += commands_content
        context += "\n```\n"

    context += "\n\n As a brief explanation of the above files: \n"
    context += "These files are used to define a small formal language for specifying geometric constructions.\n"
    context += "geo_types.py contains the definitions of geometric types which are part of these constructions."
    context += "commands.py contains the definitions of the various commands in the geometric constructions. Of particular interest is 'measure', which may be roughly translated in natural language as 'output the specified quantity'.\n"
    context += "Another example of a command is 'point_pm', which constructs a point of a specific distance from an existing point. \n"
    context += "Finally, measure_test.py provides end-to-end examples of parsing and executing the commands in the geometric constructions, as well as testing the constructions to see if they constrain the quantity of the variable named by the 'measure' command.\n"
    context += "random_constr.py, similarly, provides some examples and important functions."
    context += "The above files are mostly provided to give you an understanding of the command language, and the types of constructions that are possible. Whenever necessary, refer to geo_types.py and commands.py for the exact syntax and semantics of the commands.\n"
    context += "Your task is to translate a geometric construction file into a natural language description of the construction in the imperative mood, phrased as an AIME-style problem statement."
    context += "An AIME-style problem asks for the value of a specific quantity, as opposed to asking for a proof of a geometrical property. \n"
    context += "Contrary to the usual AIME convention that the answer must be an integer, it is acceptable to provide a rationally expressed answer, or ask for the answer as a floating-point number rounded to three decimal places.\n"
    context += "It is not necessary for you to actually solve the problem once you have translated it into natural language. Please state only your translation, with no other commentary or affirmations. \n"
    context += "Here is an example of a translation: \n"
    context += "```\n"
    context += "Input file: \n"
    context += "```\n"
    context += "# Create initial point\n"
    context += "point :  -> A\n"
    context += "# Create second point at distance 8 from A\n"
    context += "const int 8 -> side1\n"
    context += "point_pm : A side1 -> B\n"
    context += "# Create third point at distances 6 from A and 7 from B\n"
    context += "const int 6 -> side2\n"
    context += "const int 7 -> side3\n"
    context += "point_pmpm : A side2 B side3 -> C\n"
    context += "# Create the angle bisector from A\n"
    context += "angular_bisector_ppp : B A C -> bisector\n"
    context += "# Find where the angle bisector intersects BC\n"
    context += "line_pp : B C -> side_BC\n"
    context += "intersect_ll : bisector side_BC -> D\n"
    context += "# Measure the length of the angle bisector\n"
    context += "distance_pp : A D -> bisector_length\n"
    context += "# Output the final measurement\n"
    context += "measure : bisector_length -> result \n"
    context += "```\n"
    context += "Output: \n"
    context += "In triangle ABC, AB = 8, AC = 6, and BC = 7. Let D be the point where the angle bisector from A meets side BC. Find the length of segment AD. \n"
    context += "```\n"
    return context
context = create_context()

def setup_openai_client() -> OpenAI:
    """
    Set up and return an OpenAI client.
    
    Returns:
        An initialized OpenAI client
    """
    # Load environment variables from .env file
    dotenv.load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
    
    # Initialize the client
    client = OpenAI(api_key=api_key)
    return client
client = setup_openai_client()

def generate_problem(
    prompt: str,
    model: str = "o4-mini",
    max_completion_tokens: int = 10000,
    retry_attempts: int = 3,
    retry_delay: int = 5
) -> Optional[str]:
    """
    Make an API call to OpenAI with retry logic.
    
    Args:
        prompt: The text prompt to send to the API
        model: The model to use for generation
        max_completion_tokens: Maximum number of tokens to generate
        retry_attempts: Number of retry attempts on failure
        retry_delay: Delay between retries in seconds
    
    Returns:
        The generated text or None if all attempts fail
    """
    for attempt in range(retry_attempts):
        try:
            messages = []
        
            # Add system message with context if provided
            if context:
                messages.append({"role": "system", "content": context})
            
            # Add user message
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"API call failed (attempt {attempt+1}/{retry_attempts}): {str(e)}")
            if attempt < retry_attempts - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All retry attempts failed.")
                return None


def process_file_contents(filename: str, contents: str, answer: str, output_dir: Path, hash: str) -> None:
    print(f"Processing file: {filename}")
    problem = generate_problem(contents)
    if problem is None:
        return
    with open(os.path.join(output_dir, f"{global_timestamp}.jsonl"), 'a') as f:
        f.write(json.dumps({"question": problem, "answer": answer, "hash": hash, "original_filename": filename}) + "\n")


def process_timestamp_dirs(output_dir: Path, after: Optional[int] = None, hashes: Dict[str, bool] = {}) -> None:
    """
    Search the 'passed' directory for subdirectories that look like timestamps
    and process their contents if they come after the specified timestamp.
    
    Args:
        after: Optional timestamp to filter directories (process only dirs with 
               timestamps greater than this value)
    """
    passed_dir = "passed"
    
    # Get all subdirectories that look like timestamps
    timestamp_dirs = []
    for item in os.listdir(passed_dir):
        item_path = os.path.join(passed_dir, item)
        if os.path.isdir(item_path) and item.isdigit():
            timestamp = int(item)
            if after is None or timestamp > after:
                timestamp_dirs.append((timestamp, item_path))
    
    # Sort directories by timestamp
    timestamp_dirs.sort()
    
    # Process each directory
    for timestamp, dir_path in timestamp_dirs:
        print(f"Processing directory: {dir_path} (timestamp: {timestamp})")
        # Process all files in the directory
        with open(os.path.join(dir_path, "answers.txt"), 'r') as f:
            answer_lines = f.read().strip().split("\n")
        for file_path in glob.glob(os.path.join(dir_path, "*.txt")):
            if "answers.txt" in file_path:
                continue
            filename = os.path.basename(file_path)
            contents = open(file_path, 'r').read()
            hash = hashlib.sha256(contents.encode()).hexdigest()
            if hash in hashes:
                continue
            for line in answer_lines:
                if line.startswith(filename):
                    answer = line.split(" ")[1]
                    break
            process_file_contents(filename, contents, answer, output_dir, hash)

def read_hashes(output_dir: Path) -> Dict[str, bool]:
    hashes = {}
    for file in os.listdir(output_dir):
        if file.endswith(".jsonl"):
            with open(os.path.join(output_dir, file), 'r') as f:
                for line in f:
                    data = json.loads(line)
                    hashes[data["hash"]] = True
    return hashes

def main() -> None:

    parser = argparse.ArgumentParser(description="Process timestamp directories in the 'passed' folder.")
    parser.add_argument("--after", type=int, default=None, 
                        help="Only process directories with timestamps after this value")
    parser.add_argument("--output_dir", type=Path, default=Path("natural_language_problems"), 
                        help="Place to dump translated files.")
    parser.add_argument("--nohashcheck", action="store_false", dest="hash_check",
                        help="Disable hash checking")
    args = parser.parse_args()
    hashes = read_hashes(args.output_dir)
    process_timestamp_dirs(args.output_dir, args.after, hashes)


if __name__ == "__main__":
    main()