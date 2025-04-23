import numpy as np
np.seterr(all='raise') # RuntimeWarnings like divide by zero, degenerate determinants, etc. will now raise exceptions, invalidating some constructions.
import random
import inspect
import sys
import os
import argparse
from typing import Dict, List, Set, Tuple, Any, Union, Optional, Generator
import pdb

# Import the commands module
import commands
import geo_types as gt
from geo_types import MEASURABLE_TYPES

# Import required functions from random_constr.py directly
from random_constr import Command, Element, ConstCommand

class Node:
    """A node in the dependency graph representing an Element."""
    def __init__(self, element: Element, command: Optional[Command] = None):
        self.element = element
        self.command = command  # Command that generated this element
        self.parents = []  # Elements used as arguments to create this element
        self.ancestor_count = 0  # Number of ancestors (computed during dependency graph construction)
        
    def add_parent(self, parent_node: 'Node'):
        """Add a parent node (argument used to create this element)."""
        if parent_node not in self.parents:
            self.parents.append(parent_node)
            
    def __repr__(self):
        parent_labels = [p.element.label for p in self.parents]
        return f"Node({self.element.label}, parents={parent_labels}, ancestors={self.ancestor_count})"

class DependencyGraph:
    """A directed graph tracking Element dependencies in constructions."""
    def __init__(self):
        self.nodes = {}  # Maps element label to Node object
        
    def add_node(self, element: Element, command: Optional[Command] = None) -> Node:
        """Add a node to the graph."""
        if element.label not in self.nodes:
            self.nodes[element.label] = Node(element, command)
        return self.nodes[element.label]
        
    def add_dependency(self, child_element: Element, parent_elements: List[Element], command: Command):
        """
        Add a dependency relationship: child depends on parents through command.
        If nodes don't exist, they will be created.
        
        Args:
            child_element: Element for the child node
            parent_elements: List of parent elements
            command: The Command object that created the child element
        """
        # Ensure all nodes exist
        child_node = self.add_node(child_element, command)
        
        # Add parents
        for parent_element in parent_elements:
            parent_node = self.add_node(parent_element)
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
    
    def get_ancestors(self, element_label: str) -> Set[Element]:
        """Get all ancestors (direct and indirect parents) of a node."""
        if element_label not in self.nodes:
            return set()
            
        ancestors = set()
        to_process = [self.nodes[element_label]]
        processed = set()
        
        while to_process:
            current = to_process.pop()
            if current in processed:
                continue
                
            processed.add(current)
            for parent in current.parents:
                ancestors.add(parent.element)
                if parent not in processed:
                    to_process.append(parent)
                    
        return ancestors
    
    def __repr__(self):
        return f"DependencyGraph with {len(self.nodes)} nodes"

class ClassicalGenerator:
    def __init__(self, seed=None):
        """Initialize the generator with a random seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Initialize a pool of identifiers to use
        # bonus: rework this just so that polygons are labeled with conseuctive letters 
        self.identifier_pool = [chr(i) for i in range(65, 91)]  # A-Z
        random.shuffle(self.identifier_pool)
        extras = [f"{chr(i)}{j}" for i in range(65, 91) for j in range(1, 10)]  # A1-Z9
        random.shuffle(extras)
        self.identifier_pool += extras
        
        # Keep track of used identifiers and their types
        self.identifiers: Dict[str, Element] = {}
        
        # Get all available commands from the commands module
        self.available_commands = self._get_commands()
        
        # Command sequence
        self.command_sequence = []  # Now stores Command objects
        
        # Dependency graph
        self.dependency_graph = None
        
        # Pruned command sequence
        self.pruned_command_sequence = None

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
        return value_type == required_type or required_type == Any

    def _find_compatible_elements(self, required_type) -> List[Element]:
        """Find elements that have compatible types with the required type."""
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
                
        # First try to find existing compatible elements
        for identifier, element in self.identifiers.items():
            actual_type = type(element.data)
            if self._is_compatible_type(actual_type, required_type):
                compatible.append(element)
        
        # If this is a numeric type (int or float)
        if numeric_type is not None:
            # Create a new constant with probability 0.8, even if compatible elements exist
            if not compatible or random.random() < 0.8:
                # Create a new constant with a random value
                if numeric_type == int:
                    value = random.randint(1, 10)
                    element, const_command = self._add_constant('int', value)
                    # Return the newly created element
                    return [element]
                else:  # float
                    value = round(random.uniform(1, 5), 1)
                    element, const_command = self._add_constant('float', value)
                    # Return the newly created element
                    return [element]
        
        return compatible
    
    def _try_apply_command(self, cmd_name: str, input_elements: List[Element]) -> Tuple[bool, List[Element], Command]:
        """
        Try to execute a command and return its result.
        
        Args:
            cmd_name: Name of the command to execute
            input_elements: List of Element objects containing the input data
            
        Returns:
            Tuple of (success, output_elements, command):
            - success: Boolean indicating if the command executed successfully
            - output_elements: List of output Element objects if successful, empty list otherwise
            - command: The Command object that was executed
        """
        try:
            command = Command(cmd_name, input_elements, label_factory=self._get_unused_identifier, label_dict=self.identifiers)
            command.apply()
            return True, command
        except Exception as e:
            return False, None

    def _sample_commands(self) -> Generator[str, None, None]:
        # Shuffle commands to try
        command_names = list(self.available_commands.keys())
        random.shuffle(command_names)
        
        for cmd_name in command_names:
            if 'prove' in cmd_name or 'measure' in cmd_name:
                continue # these are special commands, not part of constructions
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
            if cmd_info['return_type'] == gt.Boolean:
                continue
            yield cmd_name

    def _execute_new_command(self) -> Tuple[List[Element], Command]:
        """
        Sample a random command that can be executed with existing elements.
        Returns a tuple of (input_elements, command) or None if no valid command can be sampled.
        """

        for cmd_name in self._sample_commands():
            cmd_info = self.available_commands[cmd_name]
            param_types = cmd_info['param_types']

            # Special case for commands that create points without parameters
            if cmd_name == 'point_' and len(param_types) == 0:
                # Try to execute the command directly
                success, command = self._try_apply_command(cmd_name, [])
                if success:
                    return [], command
                else:
                    continue

            # Skip commands that need parameters if we don't have any elements yet
            if not self.identifiers and param_types and not all(t in (int, float) for t in param_types):
                continue
                
            # Try to find compatible parameters, ensuring they are unique
            valid_params = True
            input_elements = []
            used_elements = set()  # Track used elements to ensure uniqueness
            
            for param_type in param_types:
                compatible = self._find_compatible_elements(param_type)
                
                if not compatible:
                    valid_params = False
                    break
                
                # Filter out already used elements
                available_elements = [elem for elem in compatible if elem not in used_elements]
                if not available_elements:
                    valid_params = False
                    break
                
                # Select a random compatible element
                selected = random.choice(available_elements)
                input_elements.append(selected)
                used_elements.add(selected)  # Mark as used
            
            if valid_params:
                # Try to execute the command
                success, command = self._try_apply_command(cmd_name, input_elements)
                if success:
                    return input_elements, command
                else:
                    continue
        # we should never get here

    def _update_dependency_graph(self, command: Command, input_elements: List[Element], output_elements: List[Element]) -> None:
        if not self.dependency_graph:
            return
            
        # Add dependencies to the graph
        for result_elem in output_elements:
            # Add node and dependencies
            self.dependency_graph.add_node(result_elem, command)
            self.dependency_graph.add_dependency(result_elem, input_elements, command)

    def _add_constant(self, const_type: str, value: Any) -> Tuple[Element, ConstCommand]:
        identifier = self._get_unused_identifier()
        
        # Create the element
        element = Element(identifier, self.identifiers)
        
        if const_type == 'int':
            data = int(value)
        elif const_type == 'float':
            data = float(value)
        
        # Create the ConstCommand
        const_command = ConstCommand(type(data), value, element)
        
        # Apply the command to set the data
        const_command.apply()
        
        # Add to command sequence
        self.command_sequence.append(const_command)
        
        # Add to dependency graph
        if self.dependency_graph:
            self.dependency_graph.add_node(element, const_command)
            self.dependency_graph.add_dependency(element, [], const_command)
            
        return element, const_command

    def generate_construction(self, num_commands: int = 5) -> List[Command]:
        """Generate a sequence of commands to form a valid construction."""
        # Initialize the dependency graph
        self.dependency_graph = DependencyGraph()
        commands_added = 0
        
        # We need to start with a point
        success, command = self._try_apply_command('point_', [])
        self.command_sequence.append(command)
        
        # Add to dependency graph
        input_elements = []
        self._update_dependency_graph(command, input_elements, command.output_elements)
        
        commands_added += 1
        
        # Try to add commands until we reach the target
        max_attempts = 100  # Prevent infinite loops
        attempt = 0
        
        while commands_added < num_commands and attempt < max_attempts:
            attempt += 1
            
            # Sample a command that can be executed
            cmd_sample = self._execute_new_command()
            if cmd_sample is None:
                continue
                
            input_elements, command = cmd_sample
            
            # Add the command to our sequence
            self.command_sequence.append(command)
            
            # Update dependency graph
            self._update_dependency_graph(command, input_elements, command.output_elements)
            
            commands_added += 1
        
        # Add a measure command at the end, choosing a measurable value
        measurable_elements = []
        
        for element in self.identifiers.values():
            # Check if the element's data type is in MEASURABLE_TYPES
            if any(isinstance(element.data, m_type) for m_type in MEASURABLE_TYPES):
                measurable_elements.append(element)
        
        if measurable_elements:
            measure_target = random.choice(measurable_elements)
            
            # Try to execute the measure command
            success, command = self._try_apply_command('measure', [measure_target])
            
            if success:
                # Add the measure command
                self.command_sequence.append(command)
                
                # Update dependency graph
                self._update_dependency_graph(command, [measure_target], command.output_elements)
        
        # Set pruned_command_sequence to the full sequence for now
        self.pruned_command_sequence = self.command_sequence.copy()
        
        return self.command_sequence

    def compute_longest_construction(self):
        """
        Find the measurable quantity with the most ancestors and create a pruned
        construction sequence that includes only the commands needed to construct it.
        """
        if not self.dependency_graph:
            self.pruned_command_sequence = self.command_sequence.copy()
            return
            
        # Find all measurable quantities
        measurable_nodes = []
        for label, node in self.dependency_graph.nodes.items():
            element = node.element
            # Check if the element's data is a measurable type
            if any(isinstance(element.data, m_type) for m_type in MEASURABLE_TYPES):
                measurable_nodes.append(node)
        
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
            if node.element.label in visited:
                return
                
            visited.add(node.element.label)
            
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
        # Create a new measure command for the target element
        measure_command = Command('measure', [target_node.element], label_factory=self._get_unused_identifier, label_dict=self.identifiers)
        measure_command.apply()
        ordered_commands.append(measure_command)
        
        # Set the pruned command sequence
        self.pruned_command_sequence = ordered_commands

    def save_construction(self, filename: str, description: str = "Generated construction"):
        with open(filename, 'w') as f:
            f.write(f"# {description}\n")
            for cmd in self.pruned_command_sequence:
                f.write(f"{cmd}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate classical geometric constructions")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--num_commands", type=int, default=25, help="Number of commands to generate")
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
