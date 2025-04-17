# "Geometry construction" dataset builder

## Pipeline

- generator.py: make candidate construction files -> generated_constructions
- check_construction_files.py: analysis / statistics of generated files, to try to make a better generator
- measure_test.py: attempt to construct the files; filter for the ones that encode legitimate constructions and compute the answers -> passed/, failed/ (40% success rate)
- translate_to_nl.py: translate the files in passed/ to natural language -> natural_language_problems/
- validator.py: quality check the natural language problems by just cross-checking with o4-mini (-> output.jsonl):  (90% success rate)
- grader.py: grade problems by difficulty (-> graded.jsonl)

## Core files (inherited from pyggb repo)
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

