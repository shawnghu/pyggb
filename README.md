# "Geometry construction" dataset builder

## Just make problems
`python pipeline.py --count 100000 --generator_class ClassicalGenerator --num_generator_commands 50 --multiprocess`

Output file is a .jsonl containing a problem, an answer in decimal to four decimal places, and various problem metadata.

## Make problems with specific properties
add arg e.g, `--generator_command_types triangle` to the above command

for options, see classical_generator.py's `parse_args()`. currently they are `basic`, `triangle`, `circle`, `polygon`, `angle`, `all`.

to see which commands are in each category, see sample_config.py.

## Grade problems

`python grader.py <file_that_was_output_by_pipeline>`

Grader takes about an hour to grade 1000 problems with qwen, 10 times as long for openthinker (since it's a reasoning model).

To speed things up with multiple GPUs try something like
`CUDA_VISIBLE_DEVICES=0,1,2,3 python grader.py --tensor_parallel_size 4 <file_that_was_output_by_pipeline>`

Tensor parallel size must be smaller than the number of GPUs and also a power of 2, so it's usually 4.

Output is a .jsonl in the same directory with an extension to the basename, and a field is added indicating the model's score on the problem and a tentative rating.


Notes:
- Above, 100000 is the number of problems that will attempt generation. Many of them will be discarded as invalid, and the success rate is between 1 and 5%, so this will only produce a few thousand valid problems.
- Likewise, 50 is the number of commands that the generator will complete, but not all of them will be used in the final problem. This is likely to produce a problem between 5 and 15 commands long.
- Due to the randomly generative nature of this repo, there is not a clear way to produce problems of a given difficulty, instead, we have to filter the questions by difficulty after grading. The only proxy for difficulty we have control over is the problem length (num_generator_commands).




## Pipeline

- classical_generator.py: make candidate construction files -> generated_constructions
- check_construction_files.py: analysis / statistics of generated files, to try to make a better generator
- measure_test.py: attempt to construct the files; filter for the ones that encode legitimate constructions and compute the answers -> passed/, failed/ 
- mechanical_translator.py: translate the files in passed/ to natural language -> natural_language_problems/
- grader.py: grade problems by difficulty (-> graded.jsonl)
    - works with vLLM with tensor parallelism, so best done on a huge server with a bunch of high-memory GPUs
    - grader_serial.py will work with a single GPU or even CPU, but is up to 100x slower (even assuming you have one gpu that fits a 32b model in memory)



## Other core files (inherited from pyggb repo)
- geo_types.py: defines the types, naturally:
- commands.py: defines the command language that these files are written in.
- random_constr.py: defines constructions. existed in the old repo. example "proves" validity of constructions by repeating them with different random seeds and seeing if they always agree.

- ggb_expr and other geogebra-related files are not used here.




## Alternate generator approach:
- classical_generator.py: generate random construction files from scratch, use programming-language constructs to constrain the symbols which can be sampled so that all programs are syntactically valid. (initial attempt complete, makes a few semantically valid constructions, but not very good. in development.) 
- see also development_notes.txt



