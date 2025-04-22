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
from geo_types import MEASURABLE_TYPES

class Node:
    """A node in the dependency graph representing an identifier."""
    def __init__(self, identifier: str, command: str = None, value_type: Any = None):
        self.identifier = identifier
        self.command = command  # Command that generated this identifier
        self.value_type = value_type
        self.parents = []  # Identifiers used as arguments to create this identifier
        # DO NOT USE THIS FOR NOW. ACTUALLY COMPUTING NUMBER OF ANCESTORS MAY NOT BE EXPENSIVE ENOUGH TO WORRY ABOUT.
        self.ancestor_count = 0  # Number of ancestors (computed during dependency graph construction)
        
    def add_parent(self, parent_node: 'Node'):
        """Add a parent node (argument used to create this identifier)."""
        if parent_node not in self.parents:
            self.parents.append(parent_node)
            
    def __repr__(self):
        parent_ids = [p.identifier for p in self.parents]
        return f"Node({self.identifier}, command={self.command}, parents={parent_ids}, ancestors={self.ancestor_count})"

class DependencyGraph:
    """A directed graph tracking identifier dependencies in constructions."""
    def __init__(self):
        self.nodes = {}  # Maps identifier to Node object
        
    def add_node(self, identifier: str, command: str = None, value_type: Any = None) -> Node:
        """Add a node to the graph."""
        if identifier not in self.nodes:
            self.nodes[identifier] = Node(identifier, command, value_type)
        return self.nodes[identifier]
        
    def add_dependency(self, child_id: str, parent_ids: List[str], command: str):
        """
        Add a dependency relationship: child depends on parents through command.
        If nodes don't exist, they will be created.
        
        Args:
            child_id: Identifier for the child node
            parent_ids: List of parent identifiers
            command: The full command string (e.g., "circle_pp : A B -> C")
        """
        # Ensure all nodes exist
        child_node = self.add_node(child_id, command)
        
        # Add parents
        for parent_id in parent_ids:
            parent_node = self.add_node(parent_id)
            child_node.add_parent(parent_node)
            
        # Update ancestor count for this node
        child_node.ancestor_count = self._calculate_ancestor_count(child_node)
    
    def _calculate_ancestor_count(self, node: Node) -> int:
        """
        Calculate the number of ancestors for a node.
        
        The count includes:
        - The sum of all ancestors of parent nodes
        - Plus one for each parent node itself
        """
        count = 0
        
        # Count direct parents
        direct_parents = len(node.parents)
        
        # Add the sum of all ancestors from parent nodes
        for parent in node.parents:
            count += parent.ancestor_count # I know this isn't actually correct; heuristic.
        
        # Add the direct parents count
        count += direct_parents
        
        return count
    
    def get_ancestors(self, identifier: str) -> Set[str]:
        """Get all ancestors (direct and indirect parents) of a node."""
        if identifier not in self.nodes:
            return set()
            
        ancestors = set()
        to_process = [self.nodes[identifier]]
        processed = set()
        
        while to_process:
            current = to_process.pop()
            if current in processed:
                continue
                
            processed.add(current)
            for parent in current.parents:
                ancestors.add(parent.identifier)
                if parent not in processed:
                    to_process.append(parent)
                    
        return ancestors
    
    def get_type(self, identifier: str) -> Any:
        """Get the type associated with an identifier."""
        if identifier in self.nodes:
            return self.nodes[identifier].value_type
        return None
    
    def __repr__(self):
        return f"DependencyGraph with {len(self.nodes)} nodes"

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
        
        # Dependency graph
        self.dependency_graph = None

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
        
        # Check if we need a numeric type
        numeric_type = None
        if required_type == int or required_type == float:
            numeric_type = required_type
        elif hasattr(required_type, "__origin__") and required_type.__origin__ is Union:
            # Check if any of the union types are numeric
            for t in required_type.__args__:
                if t == int or t == float:
                    numeric_type = t
                    break
                
        # First try to find existing compatible identifiers
        for identifier, value_info in self.identifiers.items():
            if self._is_compatible_type(value_info['type'], required_type):
                compatible.append(identifier)
        
        # If this is a numeric type (int or float)
        if numeric_type is not None:
            # Create a new constant with probability 0.8, even if compatible identifiers exist
            if not compatible or random.random() < 0.8:
                # Create a new constant with a random value
                if numeric_type == int:
                    value = random.randint(1, 10)
                    identifier = self._add_constant('int', value)
                else:  # float
                    value = round(random.uniform(1, 5), 1)
                    identifier = self._add_constant('float', value)
                
                # Return only the new constant, ignoring existing ones with probability 0.8
                return [identifier]
        
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
            # heuristics for not making boring things
            if 'minus' in cmd_name:
                if cmd_name != 'minus_mm':
                    continue
                if random.random() < 0.8:
                    continue
            if 'sum' in cmd_name:
                if cmd_name != 'sum_mm':
                    continue
                if random.random() < 0.8:
                    continue
            if 'ratio' in cmd_name:
                if random.random() < 0.8:
                    continue
            
            cmd_info = self.available_commands[cmd_name]
            param_types = cmd_info['param_types']
            
            # Special case for commands that create points without parameters
            if cmd_name == 'point_' and len(param_types) == 0:
                return cmd_name, [], cmd_info['return_type']
                
            # Special case for polygon command - needs at least 3 points
            if cmd_name == 'polygon':
                # Check if we have at least 3 point identifiers
                point_identifiers = [
                    ident for ident, info in self.identifiers.items() 
                    if self._is_compatible_type(info['type'], gt.Point)
                ]
                
                if len(point_identifiers) < 3:
                    continue  # Skip polygon command if we don't have enough points
                
                # Choose at least 3 and up to 12 unique point identifiers
                num_points = min(random.randint(3, 12), len(point_identifiers))
                selected_points = []
                
                # Shuffle and pick points
                random.shuffle(point_identifiers)
                selected_points = point_identifiers[:num_points]
                
                return cmd_name, selected_points, cmd_info['return_type']
                
            # Skip commands that need parameters if we don't have any identifiers yet
            # (except for numeric parameters which will be auto-generated)
            if not self.identifiers and param_types and not all(t in (int, float) for t in param_types):
                continue
                
            # Try to find compatible parameters, ensuring they are unique
            valid_params = True
            param_identifiers = []
            used_identifiers = set()  # Track used identifiers to ensure uniqueness
            
            for param_type in param_types:
                # Find compatible identifiers that haven't been used yet in this command
                compatible = [
                    ident for ident in self._find_compatible_identifiers(param_type)
                    if ident not in used_identifiers
                ]
                
                if not compatible:
                    valid_params = False
                    break
                
                # Select a random compatible identifier
                selected = random.choice(compatible)
                param_identifiers.append(selected)
                used_identifiers.add(selected)  # Mark as used
            
            if valid_params:
                return cmd_name, param_identifiers, cmd_info['return_type']
        # we are never supposed to get here-- it is always possible to construct a point
        return None

    def _format_command(self, cmd_name: str, params: List[str], results: List[str]) -> str:
        """Format a command as a string in the expected format."""
        param_str = " ".join(params)
        result_str = " ".join(results)
        
        # Special case for point_ which has no parameters
        if cmd_name == 'point_':
            return f"{cmd_name} : -> {result_str}"
        
        return f"{cmd_name} : {param_str} -> {result_str}"

    def _handle_return_value(self, cmd_name: str, param_identifiers: List[str], return_type) -> List[str]:
        """
        Handle the return value of a command.
        Returns a list of identifiers assigned to the return values.
        """
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
                
                # Add to dependency graph - this will be done after the full command is created
                result_identifiers.append(identifier)
            
            # Create the full command string to use in the dependency graph
            full_cmd = self._format_command(cmd_name, param_identifiers, result_identifiers)
            
            # Now add dependencies to the graph with the full command
            if self.dependency_graph:
                for result_id in result_identifiers:
                    # Pass the type when creating the node dependency
                    value_type = self.identifiers[result_id]['type']
                    self.dependency_graph.add_node(result_id, full_cmd, value_type)
                    self.dependency_graph.add_dependency(result_id, param_identifiers, full_cmd)
            
            return result_identifiers
        else:
            # For single returns or Union returns, use the actual type
            # The runtime will determine which specific type gets returned
            # from a Union, so we don't need to guess
            identifier = self._get_unused_identifier()
            
            # For Union types, we should anticipate any of the possible types
            if hasattr(return_type, "__origin__") and return_type.__origin__ is Union:
                # Store the full Union type - at runtime, the actual object
                # will have one of these concrete types
                self.identifiers[identifier] = {'type': return_type}
            else:
                # For concrete types
                self.identifiers[identifier] = {'type': return_type}
            
            # Get the type for the node
            value_type = self.identifiers[identifier]['type']
            
            # Create the full command string for the dependency graph
            full_cmd = self._format_command(cmd_name, param_identifiers, [identifier])
            
            # Add to dependency graph
            if self.dependency_graph:
                # Pass the type when creating the node
                self.dependency_graph.add_node(identifier, full_cmd, value_type)
                self.dependency_graph.add_dependency(identifier, param_identifiers, full_cmd)
                
            return [identifier]

    def _add_constant(self, const_type: str, value: Any) -> str:
        """Add a constant value to the available identifiers."""
        identifier = self._get_unused_identifier()
        
        if const_type == 'int':
            self.identifiers[identifier] = {'type': int}
            command = f"const int {value} -> {identifier}"
            self.command_sequence.append(command)
        elif const_type == 'float':
            self.identifiers[identifier] = {'type': float}
            command = f"const float {value} -> {identifier}"
            self.command_sequence.append(command)
        
        # Add to dependency graph
        if self.dependency_graph:
            value_type = self.identifiers[identifier]['type']
            self.dependency_graph.add_node(identifier, command, value_type)
            self.dependency_graph.add_dependency(identifier, [], command)
            
        return identifier

    def generate_construction(self, num_commands: int = 5) -> List[str]:
        """Generate a sequence of commands to form a valid construction."""
        # Initialize the dependency graph
        self.dependency_graph = DependencyGraph()
        commands_added = 0
        
        # We need to start with a point or two
        initial_point = self._get_unused_identifier()
        self.identifiers[initial_point] = {'type': gt.Point}
        initial_cmd = f"point_ : -> {initial_point}"
        self.command_sequence.append(initial_cmd)
        
        # Add initial point to dependency graph with its type
        self.dependency_graph.add_node(initial_point, initial_cmd, gt.Point)
        self.dependency_graph.add_dependency(initial_point, [], initial_cmd)
        
        # Explicit constant creation not needed anymore - now happens on-demand
        # constant = self._add_constant('float', round(random.uniform(1, 5), 1))
        
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
            result_identifiers = self._handle_return_value(cmd_name, param_identifiers, return_type)
            
            # Format and add the command
            command_str = self._format_command(cmd_name, param_identifiers, result_identifiers)
            self.command_sequence.append(command_str)
            commands_added += 1
        
        # Add a measure command at the end, choosing a measurable value
        measurable_identifiers = []
        
        for identifier, value_info in self.identifiers.items():
            # Check if the value's type is in MEASURABLE_TYPES
            for m_type in MEASURABLE_TYPES:
                if self._is_compatible_type(value_info['type'], m_type):
                    measurable_identifiers.append(identifier)
                    break
        
        if measurable_identifiers:
            measure_target = random.choice(measurable_identifiers)
            result_id = self._get_unused_identifier()
            measure_cmd = f"measure : {measure_target} -> {result_id}"
            self.command_sequence.append(measure_cmd)
            
            # Add measure to dependency graph with its type (which is the same as the target's type)
            target_type = self.identifiers[measure_target]['type']
            self.dependency_graph.add_node(result_id, measure_cmd, target_type)
            self.dependency_graph.add_dependency(result_id, [measure_target], measure_cmd)
            
        return self.command_sequence

    def compute_longest_construction(self):
        """
        Find the measurable quantity with the most ancestors and create a pruned
        construction sequence that includes only the commands needed to construct it.
        
        This method:
        1. Identifies all measurable quantities in the graph
        2. Finds the one with the most ancestors
        3. Uses DFS on the reversed dependency graph to build the minimal set of commands needed
        4. Sets self.pruned_command_sequence to the result
        """
        if not self.dependency_graph:
            self.pruned_command_sequence = self.command_sequence.copy()
            return
            
        # Find all measurable quantities
        measurable_nodes = []
        for identifier, node in self.dependency_graph.nodes.items():
            node_type = node.value_type
            # Check if the node's type is in MEASURABLE_TYPES
            for m_type in MEASURABLE_TYPES:
                if self._is_compatible_type(node_type, m_type):
                    measurable_nodes.append(node)
                    break
        
        if not measurable_nodes:
            # If no measurable quantities found, keep the original sequence
            self.pruned_command_sequence = self.command_sequence.copy()
            return
            
        # Find the measurable quantity with the most ancestors
        target_node = max(measurable_nodes, key=lambda node: node.ancestor_count)
        
        # Collect all commands needed for this node using DFS   
        required_commands = set()  # Use a set to avoid duplicates
        visited = set()
        
        def dfs(node):
            if node.identifier in visited:
                return
                
            visited.add(node.identifier)
            
            # First visit all parents (reversed DFS)
            for parent in node.parents:
                dfs(parent)
                
            # Then add this node's command if it exists
            if node.command:
                required_commands.add(node.command)
        
        # Start DFS from the target node
        dfs(target_node)
        
        # Convert to list and sort by original command order
        command_order = {cmd: i for i, cmd in enumerate(self.command_sequence)}
        ordered_commands = sorted(required_commands, key=lambda cmd: command_order.get(cmd, float('inf')))
        
        # Add a measure command for the target node
        measure_cmd = f"measure : {target_node.identifier} -> M"
        ordered_commands.append(measure_cmd)
        
        # Set the pruned command sequence
        self.pruned_command_sequence = ordered_commands

    def save_construction(self, filename: str, description: str = "Generated construction"):

        with open(filename, 'w') as f:
            f.write(f"# {description}\n")
            for cmd in self.pruned_command_sequence:
                f.write(f"{cmd}\n")
        # print(f"Saved construction to {filename}")



def main():
    parser = argparse.ArgumentParser(description="Generate classical geometric constructions")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--num_commands", type=int, default=100, help="Number of commands to generate")
    parser.add_argument("--output_dir", type=str, default="generated_constructions/", help="Output directory")
    parser.add_argument("--count", type=int, default=20, help="Number of constructions to generate")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    for i in range(args.count):
        seed = args.seed + i if args.seed is not None else None
        generator = ClassicalGenerator(seed=seed)
        generator.generate_construction(num_commands=args.num_commands)
        
        # Prune the construction to include only essential commands
        generator.compute_longest_construction()
        
        # Create unique filename if generating multiple constructions
        filename = os.path.join(args.output_dir, f"construction_{i+1}.txt")
            
        generator.save_construction(filename, f"Generated construction #{i+1}")


if __name__ == "__main__":
    main()
