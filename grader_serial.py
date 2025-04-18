'''
May have a few small bugs / syntax errors, particularly around extracting values from answer_question_hf.
I copied this from an old version of grader.py.
'''

import os
import argparse
import json
import torch
from validator import extract_last_float, isclose, floatify
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
qwen_model_name = "Qwen/Qwen2.5-32B-Instruct"
openthinker_model_name = "microsoft/openthinker-32b"

def load_model(model_name, device="cuda:7"):
    """
    Load the Qwen2.5 model and tokenizer.
    
    Args:
        model_name: The name or path of the Qwen model to load
        device: The device to load the model on (cuda or cpu)
    
    Returns:
        tuple: (model, tokenizer)
    """
    print(f"Loading model: {model_name}")
    
    # Check if CUDA is available when device is set to cuda
    if "cuda" in device and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    # Load model - use device_map="auto" or the specific device
    if ":" in device:  # If a specific GPU is specified (e.g., "cuda:7")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use half precision to reduce memory usage
            device_map={"": device},    # Map all modules to the specified device
            trust_remote_code=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",          # Let PyTorch decide optimal mapping
            torch_dtype=torch.float16,  # Use half precision to reduce memory usage
            trust_remote_code=True
        )
    
    return model, tokenizer



def answer_question_hf(model, tokenizer, prompt, max_length=10000):
    # Format the prompt using the model's chat template
    messages = [{"role": "user", "content": prompt}]
    chat_input = tokenizer.apply_chat_template(messages, return_tensors="pt")
    
    # Move to the correct device
    input_device = next(model.parameters()).device
    chat_input = chat_input.to(input_device)
    
    with torch.no_grad():
        outputs = model.generate(
            chat_input,
            max_new_tokens=max_length,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
    
    # The model automatically knows where the assistant's response starts
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the assistant's response
    assistant_response = tokenizer.decode(outputs[0][chat_input.shape[1]:], skip_special_tokens=True)
    
    return assistant_response.strip()

def handle_json_line(args, line, model, tokenizer):
    if not line["correct"]: # handle unfiltered files: "correct" here means the oracle model got it correct, so if that didn't happen, actually the problem is probably flawed.
        return
    if args.model_shortname == "openthinker":
        if line["difficulty"] == "easy": # already graded
            return line
    prompt = floatify(line["question"])
    answer = line["original_answer"]
    num_correct = 0
    for _ in range(args.num_trials):
        generated_answer = answer_question_hf(model, tokenizer, prompt)
        extracted_answer = extract_last_float(generated_answer)
        if extracted_answer is None:
            correct = False
        else:
            correct = isclose(float(extracted_answer), float(answer))
        if args.verbose:
            print("-" * 100)
            print(f"Generated answer: {generated_answer}")
            print("-" * 100)
            print(f"Extracted answer: {extracted_answer}")
            print(f"Correct: {correct}")
        if correct:
            num_correct += 1
    if args.model_shortname == "qwen":
        if num_correct >= args.num_trials * 0.8:
            line["difficulty"] = "easy"
        else:
            line["difficulty"] = "above-easy"
        line["qwen_trials"] = args.num_trials
        line["qwen_correct_trials"] = num_correct
    elif args.model_shortname == "openthinker":
        if num_correct >= args.num_trials * 0.8:
            line["difficulty"] = "medium"
        elif num_correct >= args.num_trials * 0.2:
            line["difficulty"] = "above-medium"
        else:
            line["difficulty"] = "probably-hard"
        line["openthinker_trials"] = args.num_trials
        line["openthinker_correct_trials"] = num_correct
    # unfortunately here we run into a problem-- models significantly better than this are approximately as strong as the models that validated the problems' correctness.
    # so we can't meaningfully grade problems with these models; models should have to get these problems 100% by definition.
    return line

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--model_shortname", type=str, default="qwen")
    parser.add_argument("--num_trials", type=int, default=10)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.model_shortname == "qwen":
        model_name = qwen_model_name
    elif args.model_shortname == "openthinker":
        model_name = openthinker_model_name
    else:
        raise ValueError(f"Invalid model shortname: {args.model_shortname}")

    model, tokenizer = load_model(model_name, args.device)
    lines = [json.loads(line) for line in open(args.input_file, "r")]
    for line in tqdm(lines, desc="Processing questions"):
        line = handle_json_line(args, line, model, tokenizer) # TODO:
        if line is None:
            continue
        with open("graded_easy.jsonl", "w") as f:
            f.write(json.dumps(line) + "\n")

if __name__ == "__main__":
    main()
