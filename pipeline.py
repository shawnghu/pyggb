import pdb
import time
from pathlib import Path
import argparse
from classical_generator import main as generator_main
from classical_generator import ClassicalGenerator
from polygon_rotation_generator import PolygonRotationGenerator
from discriminator import main as discriminator_main
from mechanical_translator import main as translator_main

def parse_args():
    parser = argparse.ArgumentParser(description="Run the full geometry pipeline")
    parser.add_argument("--count", type=int, default=20, help="Number of constructions to attempt")
    parser.add_argument("--generator_class", type=str, default="ClassicalGenerator", help="Generator class to use")
    parser.add_argument("--generator_command_types", type=str, nargs="+", choices=["polygon", "circle", "triangle", "basic", "all"], default=["all"])
    parser.add_argument("--num_generator_commands", type=int, default=25, help="Number of commands to generate")
    parser.add_argument("--min_num_generator_commands", type=int, default=8, help="Minimum number of commands in the output sequence")
    parser.add_argument("--nomultiprocess", action="store_false", dest="multiprocess", help="Don't run tests in parallel")
    parser.add_argument("--max_workers", type=int, default=16, help="Maximum number of threads to use")
    parser.add_argument("--generated_constructions_dir", type=str, default="generated_constructions", help="Output directory")
    parser.add_argument("--output_translations_dir", type=Path, default=Path("natural_language_problems"), help="Output directory")
    parser.add_argument("--seed", type=int, default=None, help="Seed for the generator")
    parser.add_argument("--discriminator_num_tests", type=int, default=20, help="Number of tests to run")
    args = parser.parse_args()
    if args.generator_class == "ClassicalGenerator":
        args.generator_class = ClassicalGenerator
    elif args.generator_class == "PolygonRotationGenerator":
        args.generator_class = PolygonRotationGenerator
    else:
        raise ValueError(f"Invalid generator class: {args.generator_class}")
    args.generated_constructions_dir = Path(args.generated_constructions_dir + "_" + str(int(time.time())))
    return args

def main():
    args = parse_args()
    generator_args = argparse.Namespace(
        count=args.count,
        generator_class=args.generator_class,
        num_commands=args.num_generator_commands,
        min_num_commands=args.min_num_generator_commands,
        command_types=args.generator_command_types,
        multiprocess=args.multiprocess,
        max_workers=args.max_workers,
        output_dir=args.generated_constructions_dir,
        seed=args.seed,
    )
    generator_main(generator_args)
    
    discriminator_args = argparse.Namespace(
        path=args.generated_constructions_dir,
        num_tests=args.discriminator_num_tests,
        verbosity=0,
        move_files=True,
        multiprocess=args.multiprocess,
        max_workers=args.max_workers,
    )
    timestamp = discriminator_main(discriminator_args)
    nl_file_name = f"{timestamp}.jsonl"
    if args.generator_command_types != ["all"]:
        nl_file_name = f"{timestamp}_{'_'.join(args.generator_command_types)}.jsonl"
    translator_args = argparse.Namespace(
        input_dir=args.generated_constructions_dir,
        output_dir=args.output_translations_dir,
        timestamp=timestamp,
        interpret_timestamp_as_after=False,
        output_name=nl_file_name,
        hash_check=False,
        max_workers=args.max_workers,
        sequential=not args.multiprocess,
        translator_type="base" if args.generator_class == ClassicalGenerator else "missing_angle",
    )
    final_timestamp = translator_main(translator_args)
    print (f"Final timestamp: {final_timestamp}")

if __name__ == "__main__":
    main()