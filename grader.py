import os
import argparse
import json
import torch
from validator import extract_last_float, isclose, floatify
from transformers import AutoModelForCausalLM, AutoTokenizer
import copy

from vllm import LLM, SamplingParams

qwen_model_name = "Qwen/Qwen2.5-32B-Instruct"
openthinker_model_name = "open-thoughts/OpenThinker-32B"



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--model_shortname", type=str, default="qwen")
    parser.add_argument("--num_trials", type=int, default=10)
    parser.add_argument("--tensor_parallel_size", type=int, default=4)
    args = parser.parse_args()

    if args.model_shortname == "qwen":
        model_name = qwen_model_name
    elif args.model_shortname == "openthinker":
        model_name = openthinker_model_name
    else:
        raise ValueError(f"Invalid model shortname: {args.model_shortname}")
    
    if args.model_shortname == "qwen":
        output_file = args.input_file.replace(".jsonl", "_graded_easy.jsonl")
    elif args.model_shortname == "openthinker":
        # we want to take the "above-easy" questions and grade them
        args.input_file = args.input_file.replace(".jsonl", "_graded_easy.jsonl")
        output_file = args.input_file.replace(".jsonl", "_graded_medium.jsonl")
        

    # Load model with vLLM - uses tensor parallelism automatically
    llm = LLM(
        model=model_name,
        tensor_parallel_size=args.tensor_parallel_size,
        trust_remote_code=True,
        dtype="float16"
    )
    
    # Prepare all prompts at once for batching
    lines = [json.loads(line) for line in open(args.input_file, "r")]
    valid_lines = []
    prompts = []
    
    lines_to_prepend = []
    for line in lines:
        if not line.get("correct", True): # handle unfiltered lines
            continue
        if args.model_shortname == "openthinker" and line.get("difficulty") == "easy":
            lines_to_prepend.append(line)
            continue
            
        # Prepare multiple trials for each question
        valid_lines.append(line)

        for _ in range(args.num_trials):
            prompts.append(floatify(line["question"]))
    
    # Configure sampling parameters
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_tokens=10000
    )
    
    # Process all prompts in an optimized way
    outputs = llm.generate(prompts, sampling_params)


    with open(output_file, "w") as f, open(output_file.replace(".jsonl", "_verbose_output.jsonl"), "w") as f_debug:
        for line_idx, line in enumerate(lines_to_prepend):
            f.write(json.dumps(line) + "\n")
        for line_idx, line in enumerate(valid_lines):
            verbose_output = copy.deepcopy(line)
            question = line["question"]
            num_correct = 0
            for trial_idx in range(args.num_trials):
                output = outputs[line_idx * args.num_trials + trial_idx]
                
                generated_text = output.outputs[0].text.strip()
                extracted_answer = extract_last_float(generated_text)
                verbose_output[f"generated_text_{trial_idx}"] = generated_text
                verbose_output[f"extracted_answer_{trial_idx}"] = extracted_answer
                correct = False
                if extracted_answer is not None:
                    correct = isclose(float(extracted_answer), float(line["original_answer"]))
                if correct:
                    num_correct += 1
                    verbose_output[f"correct_{trial_idx}"] = True
                else:
                    verbose_output[f"correct_{trial_idx}"] = False

            line[f"{args.model_shortname}_trials"] = args.num_trials
            line[f"{args.model_shortname}_correct_trials"] = num_correct
            if args.model_shortname == "qwen":
                if num_correct >= args.num_trials * 0.8:
                    line["difficulty"] = "easy"
                else:
                    line["difficulty"] = "above-easy"
            elif args.model_shortname == "openthinker":
                if num_correct >= args.num_trials * 0.8:
                    line["difficulty"] = "medium"
                elif num_correct >= args.num_trials * 0.2:
                    line["difficulty"] = "above-medium"
                else:
                    line["difficulty"] = "probably-hard"
            
            f_debug.write(json.dumps(verbose_output) + "\n")
            f.write(json.dumps(line) + "\n")


if __name__ == "__main__":
    main()


'''
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
'''