import re

def extract_function_names():
    with open('commands.py', 'r') as file:
        content = file.read()
    
    # Regular expression to match function declarations
    # This pattern looks for "def" followed by a function name and parameters
    pattern = r'def\s+([a-zA-Z0-9_]+)\s*\('
    
    # Find all matches
    matches = re.findall(pattern, content)
    
    # Sort the function names alphabetically
    matches.sort()
    
    

    print(', '.join(matches))

if __name__ == "__main__":
    extract_function_names() 