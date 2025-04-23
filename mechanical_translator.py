import os
import argparse
import glob
from typing import List, Optional, Dict
from pathlib import Path
import time
import hashlib
import time
import json
import concurrent.futures
import threading
global_timestamp = str(int(time.time()))
# Add a file lock for thread-safe writing
file_lock = threading.Lock()

def generate_problem(contents: str) -> Optional[str]:
    """
    Mechanically translate a geometric construction in command language to natural language.
    
    Args:
        contents: String containing the commands in the formal language
    
    Returns:
        A string with the natural language translation of the construction
    """
    # Define templates for each command
    command_templates = {
        # Point creation
        "point_": "Construct a point {0}.",
        "point_c": "Construct a point {0} on circle {1}.",
        "point_l": "Construct a point {0} on line {1}.",
        "point_s": "Construct a point {0} on segment {1}.",
        "point_pm": "Construct a point {0} at distance {1} from point {2}.",
        "point_at_distance": "Construct a point {0} at distance {1} from point {2} in a random direction.",
        "point_at_distance_along_line": "Construct a point {0} on line {1}, at distance {2} from point {3}.",
        
        # Line creation
        "line_pp": "Construct a line {0} through points {1} and {2}.",
        "line_pl": "Construct a line {0} through point {1} parallel to line {2}.",
        "line_pr": "Construct a line {0} through point {1} parallel to ray {2}.",
        "line_ps": "Construct a line {0} through point {1} parallel to segment {2}.",
        "line_bisector_pp": "Construct the perpendicular bisector {0} of points {1} and {2}.",
        "line_bisector_s": "Construct the perpendicular bisector {0} of segment {1}.",
        
        # Orthogonal lines
        "orthogonal_line_pl": "Construct a line {0} through point {1} perpendicular to line {2}.",
        "orthogonal_line_pr": "Construct a line {0} through point {1} perpendicular to ray {2}.",
        "orthogonal_line_ps": "Construct a line {0} through point {1} perpendicular to segment {2}.",
        
        # Angular bisectors
        "angular_bisector_ll": "Construct the angle bisectors {0} of lines {1} and {2}.",
        "angular_bisector_ppp": "Construct the angle bisector {0} of angle {1}{2}{3}.",
        "angular_bisector_ss": "Construct the angle bisectors {0} of segments {1} and {2}.",
        
        # Intersections
        "intersect_ll": "Find the intersection point {0} of lines {1} and {2}.",
        "intersect_lc": "Find the intersection points {0} of line {1} and circle {2}.",
        "intersect_cc": "Find the intersection points {0} of circles {1} and {2}.",
        "intersect_cl": "Find the intersection points {0} of circle {1} and line {2}.",
        "intersect_lr": "Find the intersection point {0} of line {1} and ray {2}.",
        "intersect_ls": "Find the intersection point {0} of line {1} and segment {2}.",
        "intersect_rl": "Find the intersection point {0} of ray {1} and line {2}.",
        "intersect_rr": "Find the intersection point {0} of rays {1} and {2}.",
        "intersect_rs": "Find the intersection point {0} of ray {1} and segment {2}.",
        "intersect_sl": "Find the intersection point {0} of segment {1} and line {2}.",
        "intersect_sr": "Find the intersection point {0} of segment {1} and ray {2}.",
        "intersect_ss": "Find the intersection point {0} of segments {1} and {2}.",
        
        # Circles
        "circle_pp": "Construct a circle {0} with center {1} passing through point {2}.",
        "circle_ppp": "Construct a circle {0} passing through points {1}, {2}, and {3}.",
        "circle_pm": "Construct a circle {0} with center {1} and radius {2}.",
        "circle_ps": "Construct a circle {0} with center {1} and radius equal to the length of segment {2}.",
        
        # Segments
        "segment_pp": "Construct segment {0} from point {1} to point {2}.",
        
        # Midpoints
        "midpoint_pp": "Find the midpoint {0} of points {1} and {2}.",
        "midpoint_s": "Find the midpoint {0} of segment {1}.",
        
        # Reflections/Mirrors
        "mirror_pp": "Reflect point {0} across point {1}, and call the resulting point {2}.",
        "mirror_pl": "Reflect point {0} across line {1}, and call the resulting point {2}.",
        "mirror_pc": "Invert point {0} with respect to circle {1}, and call the resulting point {2}.",
        "mirror_lp": "Reflect line {0} across point {1}, and call the resulting line {2}.",
        "mirror_ll": "Reflect line {0} across line {1}, and call the resulting line {2}.",
        "mirror_cl": "Reflect circle {0} across line {1}, and call the resulting circle {2}.",
        "mirror_cp": "Reflect circle {0} across point {1}, and call the resulting circle {2}.",
        
        # Angles
        "angle_ppp": "Measure the angle {0} formed by points {1}, {2}, and {3}.",
        
        # Measures
        "distance_pp": "Measure the distance {0} between points {1} and {2}.",
        "radius_c": "Measure the radius {0} of circle {1}.",
        "area": "Calculate the area {0} of the polygon formed by points {1}.",
        "area_P": "Calculate the area {0} of polygon {1}.",
        
        # Ray
        "ray_pp": "Construct ray {0} starting at point {1} and passing through point {2}.",
        
        # Rotations
        "rotate_pap": "Rotate point {0} by angle {1} around point {2}, and call the resulting point {3}.",
        "rotate_pAp": "Rotate point {0} by angle {1} around point {2}, and call the resulting point {3}.",
        
        # Vectors
        "vector_pp": "Construct vector {0} from point {1} to point {2}.",
        "translate_pv": "Translate point {0} by vector {1}, and call the resulting point {2}.",
        
        # Arithmetic operations
        "sum_mm": "Calculate the sum {0} of measures {1} and {2}.",
        "sum_ms": "Calculate the sum {0} of measure {1} and the length of segment {2}.",
        "sum_ss": "Calculate the sum {0} of the lengths of segments {1} and {2}.",
        "minus_mm": "Calculate the difference {0} between measures {1} and {2}.",
        "minus_ms": "Calculate the difference {0} between measure {1} and the length of segment {2}.",
        "minus_sm": "Calculate the difference {0} between the length of segment {1} and measure {2}.",
        "minus_ss": "Calculate the difference {0} between the lengths of segments {1} and {2}.",
        "ratio_mm": "Calculate the ratio {0} of measure {1} to measure {2}.",
        "power_mi": "Calculate the power {0} of measure {1} to the exponent {2}.",
        "power_si": "Calculate the power {0} of the length of segment {1} to the exponent {2}.",
        
        # Tangents
        "tangent_pc": "Construct the tangent lines {0} from point {1} to circle {2}.",
        "polar_pc": "Construct the polar line {0} of point {1} with respect to circle {2}.",
        
        # Boolean tests
        "are_collinear_ppp": "Test if points {1}, {2}, and {3} are collinear, and store the result in {0}.",
        "are_concurrent_lll": "Test if lines {1}, {2}, and {3} are concurrent, and store the result in {0}.",
        "are_concurrent": "Test if objects {1}, {2}, and {3} are concurrent, and store the result in {0}.",
        "are_concyclic_pppp": "Test if points {1}, {2}, {3}, and {4} are concyclic, and store the result in {0}.",
        "are_congruent_aa": "Test if angles {1} and {2} are congruent, and store the result in {0}.",
        "are_complementary_aa": "Test if angles {1} and {2} are complementary, and store the result in {0}.",
        "are_congruent_ss": "Test if segments {1} and {2} are congruent, and store the result in {0}.",
        "are_equal_mm": "Test if measures {1} and {2} are equal, and store the result in {0}.",
        "are_equal_mi": "Test if measure {1} equals the integer {2}, and store the result in {0}.",
        "are_equal_pp": "Test if points {1} and {2} are equal, and store the result in {0}.",
        "are_parallel_ll": "Test if lines {1} and {2} are parallel, and store the result in {0}.",
        "are_parallel_ls": "Test if line {1} and segment {2} are parallel, and store the result in {0}.",
        "are_parallel_rr": "Test if rays {1} and {2} are parallel, and store the result in {0}.",
        "are_parallel_sl": "Test if segment {1} and line {2} are parallel, and store the result in {0}.",
        "are_parallel_ss": "Test if segments {1} and {2} are parallel, and store the result in {0}.",
        "are_perpendicular_ll": "Test if lines {1} and {2} are perpendicular, and store the result in {0}.",
        "are_perpendicular_lr": "Test if line {1} and ray {2} are perpendicular, and store the result in {0}.",
        "are_perpendicular_rl": "Test if ray {1} and line {2} are perpendicular, and store the result in {0}.",
        "are_perpendicular_sl": "Test if segment {1} and line {2} are perpendicular, and store the result in {0}.",
        "are_perpendicular_ls": "Test if line {1} and segment {2} are perpendicular, and store the result in {0}.",
        "are_perpendicular_ss": "Test if segments {1} and {2} are perpendicular, and store the result in {0}.",
        
        # Constants
        "const": "Define a constant value {0} = {1}.",
        "const int": "Define a constant integer {0} = {1}.",
        
        # Final measurement
        "measure": "Calculate and output the value of {1} as the answer {0}."
    }
    
    # Initialize the result list
    result_lines = []
    
    # Process each line
    for line in contents.strip().split('\n'):
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Split the line into command and arguments
        parts = line.split(':')
        if len(parts) < 2:
            continue
            
        cmd = parts[0].strip()
        
        # Split arguments into inputs and outputs
        args_parts = parts[1].split('->')
        if len(args_parts) < 2:
            continue
            
        inputs = [arg.strip() for arg in args_parts[0].split() if arg.strip()]
        outputs = [arg.strip() for arg in args_parts[1].split() if arg.strip()]
        
        # Get the template for this command
        template = command_templates.get(cmd)
        if not template:
            # Skip unknown commands
            continue
        
        # Combine inputs and outputs for formatting
        format_args = outputs + inputs
        
        # Format the template with the arguments
        try:
            translated_line = template.format(*format_args)
            result_lines.append(translated_line)
        except Exception as e:
            # Skip lines that can't be formatted properly
            raise # for now
            # continue
    
    # Combine all translated lines into a coherent problem statement
    if not result_lines:
        return None
        
    final_result = " ".join(result_lines)
    
    # Add a conclusion based on the last line (which should be a measurement)
    # This assumes the last line is a "measure" command
    return final_result

def process_file_contents(filename: str, contents: str, answer: str, output_dir: Path, hash: str) -> None:
    print(f"Processing file: {filename}")
    problem = generate_problem(contents)
    if problem is None:
        return
    with file_lock:  # Use a lock to ensure thread-safe file writing
        with open(os.path.join(output_dir, f"{global_timestamp}_mechanically_translated.jsonl"), 'a') as f:
            f.write(json.dumps({"question": problem, "answer": answer, "hash": hash, "original_filename": filename}) + "\n")


def process_timestamp_dirs(output_dir: Path, after: Optional[int] = None, hashes: Dict[str, bool] = {}, max_workers: int = 4) -> None:
    """
    Search the 'passed' directory for subdirectories that look like timestamps
    and process their contents if they come after the specified timestamp.
    
    Args:
        after: Optional timestamp to filter directories (process only dirs with 
               timestamps greater than this value)
        hashes: Dictionary of file hashes that have already been processed
        max_workers: Maximum number of parallel workers to use
    """
    passed_dir = "passed"
    
    # Get all subdirectories that look like timestamps
    timestamp_dirs = []
    for item in os.listdir(passed_dir):
        item_path = os.path.join(passed_dir, item)
        if os.path.isdir(item_path) and item.isdigit():
            timestamp = int(item)
            if after is None or timestamp > after:
                timestamp_dirs.append((timestamp, item_path))
    
    # Sort directories by timestamp
    timestamp_dirs.sort()
    
    # Create a list to hold all tasks
    all_tasks = []
    
    # Process each directory
    for timestamp, dir_path in timestamp_dirs:
        print(f"Processing directory: {dir_path} (timestamp: {timestamp})")
        # Process all files in the directory
        with open(os.path.join(dir_path, "answers.txt"), 'r') as f:
            answer_lines = f.read().strip().split("\n")
        for file_path in glob.glob(os.path.join(dir_path, "*.txt")):
            if "answers.txt" in file_path:
                continue
            filename = os.path.basename(file_path)
            contents = open(file_path, 'r').read()
            hash = hashlib.sha256(contents.encode()).hexdigest()
            if hash in hashes:
                continue
            for line in answer_lines:
                if line.startswith(filename):
                    answer = line.split(" ")[1]
                    break
            all_tasks.append((f"{dir_path}/{filename}", contents, answer, output_dir, hash))
    
    # Process all tasks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file_contents, *task): task[0] for task in all_tasks}
        for future in concurrent.futures.as_completed(futures):
            filename = futures[future]
            try:
                future.result()
                print(f"Completed processing: {filename}")
            except Exception as exc:
                print(f"Processing of {filename} generated an exception: {exc}")

def read_hashes(output_dir: Path) -> Dict[str, bool]:
    hashes = {}
    for file in os.listdir(output_dir):
        # bit hacky-- heuristic to ignore files that are filtered, e.g, _validated.jsonl files
        if file.endswith(".jsonl") and not "_" in file:
            with open(os.path.join(output_dir, file), 'r') as f:
                for line in f:
                    data = json.loads(line)
                    hashes[data["hash"]] = True
    return hashes

def main() -> None:
    parser = argparse.ArgumentParser(description="Process timestamp directories in the 'passed' folder.")
    parser.add_argument("--after", type=int, default=None, 
                        help="Only process directories with timestamps after this value")
    parser.add_argument("--output_dir", type=Path, default=Path("natural_language_problems"), 
                        help="Place to dump translated files.")
    parser.add_argument("--nohashcheck", action="store_false", dest="hash_check",
                        help="Disable hash checking")
    parser.add_argument("--max_workers", type=int, default=16,
                        help="Maximum number of parallel workers")
    args = parser.parse_args()
    hashes = read_hashes(args.output_dir) if args.hash_check else {}
    process_timestamp_dirs(args.output_dir, args.after, hashes, args.max_workers)


if __name__ == "__main__":
    main()