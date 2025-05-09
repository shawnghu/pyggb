import os
# os.environ["VLLM_ATTENTION_BACKEND"] = "FLASHINFER"
# os.environ["VLLM_FLASHINFER_FORCE_TENSOR_CORES"] = "1" # https://github.com/vllm-project/vllm/issues/9471 ; still slower than simply not using flashinfer for attention
import argparse
import json
import torch
from validator import extract_last_float, isclose, floatify
import copy
import pdb
from openai import OpenAI
from vllm import LLM, SamplingParams
# from vllm.engine.arg_utils import HfOverrides

qwen_model_name = "Qwen/Qwen2.5-32B-Instruct"
qwen_7b_model_name = "Qwen/Qwen2.5-7B-Instruct"
qwen_7b_reasoning_model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

def do_inference_in_process(args, model_name, prompts):
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
        gpu_memory_utilization=args.gpu_memory_utilization
    )
    # Configure sampling parameters
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_tokens=10000,
    )
    
    outputs = llm.generate(prompts, sampling_params)
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--model_shortname", type=str, default="qwen")
    parser.add_argument("--tensor_parallel_size", type=int, default=1)
    parser.add_argument("--pipeline_parallel_size", type=int, default=1)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.9)
    args = parser.parse_args()
    main_with_args(args)

def main_with_args(args):
    if args.model_shortname == "qwen":
        model_name = qwen_model_name
    elif args.model_shortname == "qwen_7b":
        model_name = qwen_7b_model_name
    elif args.model_shortname == "qwen_7b_reasoning":
        model_name = qwen_7b_reasoning_model_name
    else:
        raise ValueError(f"Invalid model shortname: {args.model_shortname}")
    
    # Prepare all prompts at once for batching
    lines = [json.loads(line) for line in open(args.input_file, "r")]
    try:
        prompts = [line["question"] for line in lines]
    except KeyError:
        prompts = [line["problem"] for line in lines]
            
    outputs = do_inference_in_process(args, model_name, prompts)
    generated_texts = [output.outputs[0].text.strip() for output in outputs]


    output_file = args.input_file.replace(".jsonl", "_graded.jsonl")
    with open(output_file, "w") as f:
        for line_idx, line in enumerate(lines):
            generated_text = generated_texts[line_idx]
            extracted_answer = extract_last_float(generated_text)
            correct = False
            if extracted_answer is not None:
                try:
                    correct = isclose(float(extracted_answer), float(line["answer"]))
                except KeyError:
                    correct = isclose(float(extracted_answer), float(line["original_answer"]))
            line["correct"] = correct
            line["generated_text"] = generated_text
            line["extracted_answer"] = extracted_answer

            f.write(json.dumps(line) + "\n")


if __name__ == "__main__":
    main()
