import argparse
import json
import random
import concurrent.futures
import threading
from cost_estimator import OpenAICostEstimator
import dotenv
import os
import pdb
dotenv.load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

import openai

openai.api_key = api_key
client = openai.OpenAI()

# Add a file lock for thread-safe writing
file_lock = threading.Lock()

def floatify(text):
    return text + "\nAt the end of your response, please provide your answer expressed as a decimal number rounded to 3 decimal places."

def answer_question(cost_estimator, prompt, model="o4-mini"):
    messages = []
    prompt = floatify(prompt)
    # Add user message
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    pdb.set_trace()
    cost_estimator.handle_usage(response.usage)
    return response.choices[0].message.content

import re

def extract_last_float(text):
    """
    Extract the last floating point number from a string.
    
    Args:
        text (str): The text to search for floating point numbers
        
    Returns:    
        float or None: The last floating point number found in the text, or None if no number is found
    """
    # This regex matches decimal numbers (both with and without decimal points)
    # It handles numbers like: 123, 123.456, .456, etc.
    matches = re.findall(r'-?\d*\.?\d+', text)
    
    if matches:
        return float(matches[-1])
    else:
        return None

def isclose(a, b, abs_tol=0.011):
    return abs(a - b) <= abs_tol

def process_question(line, cost_estimator, model="o4-mini"):
    """Process a single question and return the result."""
    prompt = line["question"]
    answer = line["answer"]
    generated_answer = answer_question(cost_estimator, prompt, model)
    extracted_answer = extract_last_float(generated_answer)
    
    newjson = {
        "question": prompt,
        "generated_answer": generated_answer,
        "original_answer": answer,
        "extracted_answer": extracted_answer,
        "original_filename": line.get("original_filename", ""),
        "correct": isclose(float(extracted_answer), float(answer)) if extracted_answer is not None else False
    }
    
    return newjson

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--max_workers", type=int, default=16, 
                        help="Maximum number of parallel workers")
    parser.add_argument("--model", type=str, default="o4-mini",
                        help="Model to use for answering questions")
    args = parser.parse_args()

    cost_estimator = OpenAICostEstimator(application_name="validator", model_name=args.model)
    data = []
    with open(args.input_file, 'r') as f:
        for line in f:
            process_question(json.loads(line), cost_estimator, args.model)
            data.append(json.loads(line))

    total_correct = 0
    total_processed = 0
    
    # Process questions in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all tasks
        future_to_line = {executor.submit(process_question, line, cost_estimator, args.model): line for line in data}
        
        # Open output file outside the loop
        with open("output.jsonl", "w") as f:
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_line):
                try:
                    result = future.result()
                    # Use lock for thread-safe file writing
                    with file_lock:
                        f.write(json.dumps(result) + "\n")
                        f.flush()  # Ensure data is written immediately
                    
                    if result["correct"]:
                        total_correct += 1
                    total_processed += 1
                    
                    # Print progress
                    if total_processed % 10 == 0:
                        print(f"Processed {total_processed}/{len(data)} questions. Current accuracy: {total_correct/total_processed:.2f}")
                        
                except Exception as exc:
                    print(f"Question processing generated an exception: {exc}")
    
    print(f"Total correct: {total_correct}/{len(data)} ({total_correct/len(data):.2f})")

if __name__ == "__main__":
    main()