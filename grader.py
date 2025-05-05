import os
# os.environ["VLLM_ATTENTION_BACKEND"] = "FLASHINFER"
# os.environ["VLLM_FLASHINFER_FORCE_TENSOR_CORES"] = "1" # https://github.com/vllm-project/vllm/issues/9471 ; still slower than simply not using flashinfer for attention
import argparse
import json
import torch
from validator import extract_last_float, isclose, floatify
from transformers import AutoModelForCausalLM, AutoTokenizer
import copy
import pdb
from vllm import LLM, SamplingParams
# from vllm.engine.arg_utils import HfOverrides

qwen_model_name = "Qwen/Qwen2.5-32B-Instruct"
openthinker_model_name = "open-thoughts/OpenThinker-32B"



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--model_shortname", type=str, default="both")
    parser.add_argument("--grade_all_problems", action="store_true")
    parser.add_argument("--num_trials", type=int, default=10)
    parser.add_argument("--tensor_parallel_size", type=int, default=1)
    parser.add_argument("--pipeline_parallel_size", type=int, default=1)
    args = parser.parse_args()
    if args.model_shortname == "both":
        args.model_shortname = "qwen"
        main_with_args(args)
        args.model_shortname = "openthinker"
        main_with_args(args)
    else:
        main_with_args(args)

def main_with_args(args):
    if args.model_shortname == "qwen":
        model_name = qwen_model_name
    elif args.model_shortname == "openthinker":
        model_name = openthinker_model_name
    else:
        raise ValueError(f"Invalid model shortname: {args.model_shortname}")
    
    if args.model_shortname == "qwen":
        output_file = args.input_file.replace(".jsonl", "_graded_easy.jsonl")
    elif args.model_shortname == "openthinker":
        if args.grade_all_problems:
            output_file = args.input_file.replace(".jsonl", "_graded_special.jsonl")
        else:
            # we want to take the "above-easy" questions and grade them
            args.input_file = args.input_file.replace(".jsonl", "_graded_easy.jsonl")
            output_file = args.input_file.replace(".jsonl", "_graded_medium.jsonl")
        
    hf_overrides = {
        "use_cache": True
    }
    # Load model with vLLM - uses tensor parallelism automatically
    llm = LLM(
        model=model_name,
        tensor_parallel_size=args.tensor_parallel_size,
        pipeline_parallel_size=args.pipeline_parallel_size,
        trust_remote_code=False,
        dtype="float16",
        hf_overrides=hf_overrides,
        # enable_chunked_prefill=True,
        # max_num_batched_tokens=8192,
    )
    
    # Prepare all prompts at once for batching
    lines = [json.loads(line) for line in open(args.input_file, "r")]
    valid_lines = []
    prompts = []
    
    lines_to_prepend = []
    for line in lines:
        if not line.get("correct", True): # handle unfiltered lines
            continue
        if args.model_shortname == "openthinker" and not args.grade_all_problems and line.get("difficulty") == "easy":
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
                    try:
                        correct = isclose(float(extracted_answer), float(line["answer"]))
                    except KeyError:
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
