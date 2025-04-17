import argparse
import json
import random

import dotenv
import os
dotenv.load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

import openai

openai.api_key = api_key

client = openai.OpenAI()

def floatify(text):
    return text + "\nAt the end of your response, please provide your answer expressed as a decimal number rounded to 3 decimal places."

def answer_question(prompt, model="o4-mini"):
    messages = []
    prompt = floatify(prompt)
    # Add user message
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
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

def isclose(a, b, abs_tol=0.002):
    return abs(a - b) <= abs_tol

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()

    data = []
    with open(args.input_file, 'r') as f:
        for line in f:
            data.append(json.loads(line))

    # randomly sample 10 lines
    # sampled_lines = random.sample(data, 5)
    total_correct = 0
    with open("output.jsonl", "w") as f:
        for line in data:
            prompt = line["question"]
            answer = line["answer"]
            generated_answer = answer_question(prompt)
            extracted_answer = extract_last_float(generated_answer)
            newjson = {}
            newjson["question"] = prompt
            newjson["generated_answer"] = generated_answer
            newjson["original_answer"] = answer
            newjson["extracted_answer"] = extracted_answer
            newjson["original_filename"] = line["original_filename"]
            newjson["correct"] = isclose(float(extracted_answer), float(answer))
            f.write(json.dumps(newjson) + "\n")
            if newjson["correct"]:
                total_correct += 1
    print(f"Total correct: {total_correct}")



if __name__ == "__main__":
    main()