import os
import sys
import traceback
from random_constr import Construction

def check_constructions(directory_path, verbose=True):
    """
    Check all construction files in a directory by attempting to load them.
    Collects statistics on success/failure and prints error messages.
    
    Args:
        directory_path: Path to directory containing construction files
        verbose: Whether to print detailed error messages
    
    Returns:
        Dictionary with statistics about the loaded files
    """
    valid_files = []
    invalid_files = []
    error_types = {}
    error_details = {}
    
    # For semantically valid files (construction can run)
    semantically_valid_files = []
    semantic_errors = []
    semantic_error_types = {}
    
    # Process each .txt file in the directory
    total_files = 0
    for filename in os.listdir(directory_path):
        if not filename.endswith('.txt'):
            continue
            
        total_files += 1
        file_path = os.path.join(directory_path, filename)
        
        construction = Construction()
        try:
            construction.load(file_path)
            valid_files.append(filename)
            print(f"✓ {filename}: Successfully loaded")
            
            # Check if it's a measure file
            if construction.statement_type != "measure":
                print(f"  Note: {filename} does not end with a measure statement")
            
            # Now test for semantic validity by running the commands
            try:
                if verbose:
                    print(f"  Testing if commands can run...")
                construction.run_commands()
                
                # If we got here, the commands ran successfully
                semantically_valid_files.append(filename)
                if verbose:
                    print(f"  ✓ Commands ran successfully")
                
                # For measure statements, try to get the value
                if construction.statement_type == "measure":
                    try:
                        value = construction.to_measure.value()
                        if verbose:
                            print(f"  ✓ Measure value: {value}")
                    except Exception as e:
                        if verbose:
                            print(f"  ✗ Failed to get measure value: {str(e)}")
                
            except Exception as e:
                semantic_errors.append((filename, e))
                
                error_type = type(e).__name__
                semantic_error_types[error_type] = semantic_error_types.get(error_type, 0) + 1
                
                if verbose:
                    print(f"  ✗ Failed to run commands: {str(e)}")
                    traceback.print_exc()
            
        except Exception as e:
            invalid_files.append(filename)
            error_message = str(e)
            
            # Track error types
            error_type = type(e).__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Capture detailed error information
            tb = traceback.extract_tb(sys.exc_info()[2])
            error_line = None
            error_func = None
            error_filename = None
            error_code = None
            
            for frame in tb:
                if 'random_constr.py' in frame.filename:
                    error_line = frame.lineno
                    error_func = frame.name
                    error_filename = os.path.basename(frame.filename)
                    error_code = frame.line
                    break
            
            error_detail = {
                "line": error_line,
                "function": error_func,
                "filename": error_filename,
                "code": error_code,
                "message": error_message
            }
            
            if error_detail["code"] and error_detail["line"]:
                detail_key = f"{error_filename}:{error_line} - {error_code}"
                if detail_key not in error_details:
                    error_details[detail_key] = []
                error_details[detail_key].append(filename)
            
            # Try to read the problematic line from the construction file
            problem_line = None
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    # Check the first few non-comment, non-empty lines for syntax issues
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if not (':' in line and '->' in line) and not line.startswith('const '):
                                problem_line = f"Line {i+1}: {line}"
                                break
            except:
                pass
            
            if verbose:
                print(f"✗ {filename}: Failed to load")
                print(f"  Error: {error_message}")
                print(f"  Error location: {error_filename}:{error_line} in {error_func}")
                print(f"  Error code: {error_code}")
                if problem_line:
                    print(f"  Problematic line: {problem_line}")
                print("  Traceback:")
                traceback.print_exc()
                print("  -----------------------")
            else:
                error_loc = f"{error_filename}:{error_line}" if error_line else "unknown location"
                print(f"✗ {filename}: Failed to load - {error_type} at {error_loc}")
                if problem_line:
                    print(f"  Problematic line: {problem_line}")
    

    
    # Add semantic validation statistics
    if valid_files:
        print(f"\nOf syntactically valid files:")
        print(f"  Semantically valid (can run): {len(semantically_valid_files)} ({len(semantically_valid_files)/len(valid_files)*100:.1f}%)")
        print(f"  Semantically invalid (errors): {len(valid_files) - len(semantically_valid_files)} ({(len(valid_files) - len(semantically_valid_files))/len(valid_files)*100:.1f}%)")
    
    if error_types:
        print("\nSyntax error types:")
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count} files ({count/len(invalid_files)*100:.1f}% of errors)")
    
    if semantic_error_types:
        print("\nSemantic error types:")
        for error_type, count in semantic_error_types.items():
            print(f"  {error_type}: {count} files ({count/len(semantic_errors)*100:.1f}% of semantic errors)")
    
    if error_details:
        print("\nCommon error locations:")
        for detail, files in error_details.items():
            if len(files) > 1:
                print(f"  {detail} ({len(files)} files)")
    
    # Show samples of semantically valid files
    if semantically_valid_files:
        print("\nSample semantically valid files:")
        for filename in semantically_valid_files[:min(3, len(semantically_valid_files))]:
            print(f"  {filename}")
    
    # Show samples of problematic files
    print("\nSample syntactically invalid files:")
    for filename in invalid_files[:min(3, len(invalid_files))]:
        print(f"\n{filename}:")
        try:
            with open(os.path.join(directory_path, filename), 'r') as f:
                for i, line in enumerate(f.readlines()[:10]):  # First 10 lines
                    print(f"  {i+1}: {line.rstrip()}")
                
        except Exception as e:
            print(f"  Error reading file: {e}")
    
    # Show samples of semantically invalid files
    if semantic_errors:
        print("\nSample semantically invalid files:")
        for filename, error in semantic_errors[:min(3, len(semantic_errors))]:
            print(f"\n{filename}: {type(error).__name__}: {str(error)}")
            try:
                with open(os.path.join(directory_path, filename), 'r') as f:
                    for i, line in enumerate(f.readlines()[:10]):  # First 10 lines
                        print(f"  {i+1}: {line.rstrip()}")
                    
            except Exception as e:
                print(f"  Error reading file: {e}")

        # Print summary statistics
    print("\nSUMMARY:")
    print(f"Total files examined: {total_files}")
    print(f"Syntactically valid files: {len(valid_files)} ({len(valid_files)/total_files*100:.1f}%)")
    print(f"Syntactically invalid files: {len(invalid_files)} ({len(invalid_files)/total_files*100:.1f}%)")
    
    return {
        "total_files": total_files,
        "syntactically_valid_files": valid_files,
        "syntactically_invalid_files": invalid_files,
        "semantically_valid_files": semantically_valid_files,
        "semantic_errors": semantic_errors,
        "syntax_error_types": error_types,
        "semantic_error_types": semantic_error_types,
        "error_details": error_details
    }

if __name__ == "__main__":
    # Get directory path from command line or use default
    directory_path = sys.argv[1] if len(sys.argv) > 1 else "generated_constructions"
    
    # Check if verbose flag is provided
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Run the check
    check_constructions(directory_path, verbose) 