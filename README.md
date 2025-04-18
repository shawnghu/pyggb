# "Geometry construction" dataset builder

## Pipeline

- generator.py: make candidate construction files -> generated_constructions
- check_construction_files.py: analysis / statistics of generated files, to try to make a better generator
- measure_test.py: attempt to construct the files; filter for the ones that encode legitimate constructions and compute the answers -> passed/, failed/ (40% success rate)
- translate_to_nl.py: translate the files in passed/ to natural language -> natural_language_problems/
- validator.py: quality check the natural language problems by just cross-checking with o4-mini (-> output.jsonl):  (90% success rate)
- grader.py: grade problems by difficulty (-> graded.jsonl)
    - works with vLLM with tensor parallelism, so best done on a huge server with a bunch of high-memory GPUs
    - grader_serial.py will work with a single GPU or even CPU, but is up to 100x slower (even assuming you have one gpu that fits a 32b model in memory)

## Summary of pipeline performance/decisions:
- overall estimate a 1/3 success rate end to end, loosely assume that candidate construction files are 1000 tokens, input prompt is 10000 tokens for 100 constructions
- translation to natural language problems is maybe 3000 tokens, but happens on only semantically valid constructions, so 1000 tokens per construction
- validator uses a reasoning model, so maybe 30000 tokens, or 10000 per initial construction
- assume grader is free, which may not really be true because it can use like 6kW electricity

-> using current scheme with 4.1-mini for generation/translation, and o4-mini for validation, 10-15 cents per valid problem
-> of 89 generated problems, 65 were easy (qwen answered at least 4/5 correct), 7 were medium (openthinker answered at least 4/5 correct), 9 were "above-medium" (openthinker answered at least 1/5 correct), 0 were "probably-hard" (openthinker answered less than 1/5 correct)

- this approach may not scale cost-effectively to harder or longer problems, since probability of successful construction goes down as the problem gets longer, so try "classical" generator approach (see below).
- note that these statistics imply openthinker perhaps isn't better than qwen on these problems



## Other core files (inherited from pyggb repo)
- ggb_expr and other geogebra-related files are not used here.
- geo_types.py: defines the types, naturally:
- commands.py: defines the command language that these files are written in.
- random_constr.py: example file, which existed in the old repo. "proves" validity of constructions by repeating them with different random seeds and seeing if they always agree.


## Model selection considerations and tricks for problem generation
Currently the generator uses gpt-4.1-mini, and at time of writing has approximately a 40% success rate at at least making a file with a valid construction. More powerful models do not have an appreciably higher success rate and are costlier and slower to generate. gpt-4.1-nano has a 2-5% success rate, so is mostly not feasible for use.

There seems to be no major advantage to asking the model to generate such files 10 at a time vs 100 at a time, so do the latter.

## Ways of improving the pipeline at various points

- Simple improvements to the prompt or command language may make the generator likelier to make valid files, but I already picked the low hanging fruit here. Mostly the model is making syntactically valid files, and it is a much higher bar to expect it to make semantically valid ones (at comparable cost).
- Likewise, I am not sure how to improve the rate of natural language translation. It seems like unavoidably, some of the constructions are for pretty stupid problems, and the model "helpfully" translates them into more reasonable questions, which then do not match the original construction. Filtering with 4.1 is already relatively cheap, though.


## Alternate generator approach:
- classical_generator.py: generate random construction files from scratch, use programming-language constructs to constrain the symbols which can be sampled so that all programs are syntactically valid. (initial attempt complete, makes a few semantically valid constructions, but not very good. in development.) 
- see also development_notes.txt