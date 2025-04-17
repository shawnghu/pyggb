
import os
import argparse
import json
import torch
from validator import extract_last_float, isclose
from transformers import AutoModelForCausalLM, AutoTokenizer

qwen_model_name = "Qwen/Qwen2.5-7B-Instruct"
openthinker_model_name = "microsoft/openthinker-32b"

def load_model(model_name, device="cuda"):
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
    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map=device,
        trust_remote_code=True
    )
    
    return model, tokenizer



def answer_question_hf(model, tokenizer, prompt, max_length=10000):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the model's response (remove the prompt)
    response = response[len(tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):]
    
    return response.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="output.jsonl")
    parser.add_argument("--model_shortname", type=str, default="qwen")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    if args.model_shortname == "qwen":
        model_name = qwen_model_name
    elif args.model_shortname == "openthinker":
        model_name = openthinker_model_name
    else:
        raise ValueError(f"Invalid model shortname: {args.model_shortname}")

    model, tokenizer = load_model(model_name, args.device)

    with open("graded.jsonl", "w") as f:
        for line in open(args.input_file, "r"):
            line = json.loads(line)
            if not line["correct"]:
                f.write(json.dumps(line) + "\n")
                continue
            if args.model_shortname == "openthinker":
                if line["difficulty"] == "easy":
                    f.write(json.dumps(line) + "\n")
                    continue
            prompt = line["question"]
            answer = line["answer"]
            generated_answer = answer_question_hf(prompt)
            extracted_answer = extract_last_float(generated_answer)
            newjson = {}
            newjson["question"] = prompt
            newjson["generated_answer"] = generated_answer
            newjson["original_answer"] = answer
            newjson["extracted_answer"] = extracted_answer
            newjson["original_filename"] = line["original_filename"]
            correct = isclose(float(extracted_answer), float(answer))
            if args.model_shortname == "qwen":
                if correct:
                    newjson["difficulty"] = "easy"
                else:
                    newjson["difficulty"] = "above-easy"
            elif args.model_shortname == "openthinker":
                if correct:
                    newjson["difficulty"] = "medium"
                else:
                    newjson["difficulty"] = "above-medium"
            # unfortunately here we run into a problem-- models significantly better than this are approximately as strong as the models that validated the problems' correctness.
            # so we can't meaningfully grade problems with these models; models should have to get these problems 100% by definition.
            f.write(json.dumps(newjson) + "\n")


if __name__ == "__main__":
    main()