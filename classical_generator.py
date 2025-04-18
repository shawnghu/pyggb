import numpy as np
import random
import inspect
import sys
import os
import argparse
from typing import Dict, List, Set, Tuple, Any, Union, Optional

# Import the commands module
import commands
import geo_types as gt

class ClassicalGenerator:
    def __init__(self, seed=None):
        """Initialize the generator with a random seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Initialize a pool of identifiers to use
        self.identifier_pool = [chr(i) for i in range(65, 91)]  # A-Z
        self.identifier_pool += [f"{chr(i)}{j}" for i in range(65, 91) for j in range(1, 10)]  # A1-Z9
        
        # Keep track of used identifiers and their types
        self.identifiers: Dict[str, Any] = {}
        
        # Get all available commands from the commands module
        self.available_commands = self._get_commands()
        
        # Command sequence
        self.command_sequence = []

    def _get_commands(self) -> Dict[str, Dict]:
        """Extract all commands from the commands module with their parameter and return types."""
        commands_dict = {}
        
        for name, func in inspect.getmembers(commands, inspect.isfunction):
            if name.startswith('_'):
                continue
                
            sig = inspect.signature(func)
            
            # Get parameter types
            param_types = []
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    param_types.append(param.annotation)
                else:
                    # If no type annotation, use Any
                    param_types.append(Any)
            
            # Get return type
            return_type = sig.return_annotation if sig.return_annotation != inspect.Signature.empty else Any
            
            commands_dict[name] = {
                'func': func,
                'param_types': param_types,
                'return_type': return_type
            }
            
        return commands_dict

    def _get_unused_identifier(self) -> str:
        """Get an unused identifier from the pool."""
        for identifier in self.identifier_pool:
            if identifier not in self.identifiers:
                return identifier
        raise ValueError("Ran out of identifiers!")

    def _is_compatible_type(self, value_type, required_type) -> bool:
        """Check if a value type is compatible with a required type."""
        # Handle Union types
        if hasattr(required_type, "__origin__") and required_type.__origin__ is Union:
            return any(self._is_compatible_type(value_type, t) for t in required_type.__args__)
        
        # Check if the types match or if required_type is Any
        return value_type == required_type or required_type == Any

    def _find_compatible_identifiers(self, required_type) -> List[str]:
        """Find identifiers that have compatible types with the required type."""
        compatible = []
        for identifier, value_info in self.identifiers.items():
            if self._is_compatible_type(value_info['type'], required_type):
                compatible.append(identifier)
        return compatible

    def _sample_command(self) -> Optional[Tuple[str, List[str], Any]]:
        """
        Sample a random command that can be executed with existing identifiers.
        Returns a tuple of (command_name, parameter_identifiers, return_type) or None if no valid command can be sampled.
        """
        # Shuffle commands to try
        command_names = list(self.available_commands.keys())
        random.shuffle(command_names)
        
        for cmd_name in command_names:
            cmd_info = self.available_commands[cmd_name]
            param_types = cmd_info['param_types']
            
            # Special case for commands that create points without parameters
            if cmd_name == 'point_' and len(param_types) == 0:
                return cmd_name, [], cmd_info['return_type']
                
            # Skip commands that need parameters if we don't have any identifiers yet
            if not self.identifiers and param_types:
                continue
                
            # Try to find compatible parameters
            valid_params = True
            param_identifiers = []
            
            for param_type in param_types:
                compatible = self._find_compatible_identifiers(param_type)
                if not compatible:
                    valid_params = False
                    break
                param_identifiers.append(random.choice(compatible))
                
            if valid_params:
                return cmd_name, param_identifiers, cmd_info['return_type']
                
        return None

    def _format_command(self, cmd_name: str, params: List[str], results: List[str]) -> str:
        """Format a command as a string in the expected format."""
        param_str = " ".join(params)
        result_str = " ".join(results)
        
        # Special case for point_ which has no parameters
        if cmd_name == 'point_':
            return f"{cmd_name} : -> {result_str}"
        
        return f"{cmd_name} : {param_str} -> {result_str}"

    def _handle_return_value(self, return_type) -> List[str]:
        """
        Handle the return value of a command.
        Returns a list of identifiers assigned to the return values.
        """
        # Check if return type is a Union
        if hasattr(return_type, "__origin__") and return_type.__origin__ is Union:
            # Pick one of the possible return types
            return_type = random.choice(return_type.__args__)
            
        # Check if return type is a list
        if hasattr(return_type, "__origin__") and return_type.__origin__ is list:
            # For list returns, get the element type
            element_type = return_type.__args__[0]
            
            # Randomly choose how many elements to handle (1-3)
            num_elements = random.randint(1, 3)
            result_identifiers = []
            
            for _ in range(num_elements):
                identifier = self._get_unused_identifier()
                self.identifiers[identifier] = {'type': element_type}
                result_identifiers.append(identifier)
                
            return result_identifiers
        else:
            # For single returns
            identifier = self._get_unused_identifier()
            self.identifiers[identifier] = {'type': return_type}
            return [identifier]

    def _add_constant(self, const_type: str, value: Any) -> str:
        """Add a constant value to the available identifiers."""
        identifier = self._get_unused_identifier()
        
        if const_type == 'int':
            self.identifiers[identifier] = {'type': int}
            self.command_sequence.append(f"const int {value} -> {identifier}")
        elif const_type == 'float':
            self.identifiers[identifier] = {'type': float}
            self.command_sequence.append(f"const float {value} -> {identifier}")
            
        return identifier

    def generate_construction(self, num_commands: int = 5) -> List[str]:
        """Generate a sequence of commands to form a valid construction."""
        commands_added = 0
        
        # We need to start with a point or two
        initial_point = self._get_unused_identifier()
        self.identifiers[initial_point] = {'type': gt.Point}
        self.command_sequence.append(f"point_ : -> {initial_point}")
        
        # Add a constant for distance or size
        constant = self._add_constant('float', round(random.uniform(1, 5), 1))
        
        # Try to add commands until we reach the target
        max_attempts = 100  # Prevent infinite loops
        attempt = 0
        
        while commands_added < num_commands and attempt < max_attempts:
            attempt += 1
            
            # Sample a command that can be executed
            cmd_sample = self._sample_command()
            if cmd_sample is None:
                continue
                
            cmd_name, param_identifiers, return_type = cmd_sample
            
            # Handle return values
            result_identifiers = self._handle_return_value(return_type)
            
            # Format and add the command
            command_str = self._format_command(cmd_name, param_identifiers, result_identifiers)
            self.command_sequence.append(command_str)
            commands_added += 1
        
        # Add a measure command at the end, choosing a measurable value
        measurable_types = [gt.Measure, gt.Boolean, float, int]
        measurable_identifiers = []
        
        for identifier, value_info in self.identifiers.items():
            for m_type in measurable_types:
                if self._is_compatible_type(value_info['type'], m_type):
                    measurable_identifiers.append(identifier)
                    break
        
        if measurable_identifiers:
            measure_target = random.choice(measurable_identifiers)
            result_id = self._get_unused_identifier()
            self.command_sequence.append(f"measure : {measure_target} -> {result_id}")
            
        return self.command_sequence

    def save_construction(self, filename: str, description: str = "Generated construction"):
        """Save the generated construction to a file."""
        with open(filename, 'w') as f:
            f.write(f"# {description}\n")
            for cmd in self.command_sequence:
                f.write(f"{cmd}\n")
        print(f"Saved construction to {filename}")


def main():
    parser = argparse.ArgumentParser(description="Generate classical geometric constructions")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--num_commands", type=int, default=5, help="Number of commands to generate")
    parser.add_argument("--output_dir", type=str, default="generated_constructions/", help="Output directory")
    parser.add_argument("--count", type=int, default=20, help="Number of constructions to generate")
    args = parser.parse_args()
    
    for i in range(args.count):
        seed = args.seed + i if args.seed is not None else None
        generator = ClassicalGenerator(seed=seed)
        generator.generate_construction(num_commands=args.num_commands)
        
        # Create unique filename if generating multiple constructions
        filename = os.path.join(args.output_dir, f"construction_{i+1}.txt")
            
        generator.save_construction(filename, f"Generated construction #{i+1}")


if __name__ == "__main__":
    main()
