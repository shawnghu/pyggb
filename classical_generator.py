import functools
import numpy as np
np.seterr(all='raise') # RuntimeWarnings like divide by zero, degenerate determinants, etc. will now raise exceptions, invalidating some constructions.
import random
import inspect
import sys
import os
import argparse
from typing import Dict, List, Set, Tuple, Any, Union, Optional, Generator, Callable
import pdb
import concurrent.futures
# Import the commands module
import commands
import geo_types as gt
from geo_types import MEASURABLE_TYPES, AngleSize
from random_constr import Command, Element, ConstCommand
from sample_config import get_commands

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
        self.nodes: Dict[Element, Node] = {}

    def add_node(self, element: Element, command: Optional[Command] = None) -> Node:
        """Add a node to the graph."""
        if element not in self.nodes:
            self.nodes[element] = Node(element, command)
        return self.nodes[element]
        
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
    
    def __repr__(self):
        return f"DependencyGraph with {len(self.nodes)} nodes"

class ClassicalGenerator:
    def __init__(self, seed=None, command_types=None):
        """Initialize the generator with a random seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.init_identifier_pool()
        
        # Keep track of used identifiers and their types
        self.identifiers: Dict[str, Element] = {}
        self.identifier_queue: List[str] = []
        
        # Get all available commands from the commands module
        self.available_commands = self._get_commands()
        if command_types:
            self.available_commands = {k: v for k, v in self.available_commands.items() if k in get_commands(command_types)}

        self.command_sequence: List[Command] = []
        self.dependency_graph = DependencyGraph()
        self.pruned_command_sequence: List[Command] = []
        self.made_polygon_already: bool = False
        self.made_triangle_already: bool = False
        self.element_to_constructed_command: Dict[Element, Command] = {}
        # this has to exist because when we construct a polygon, the vertices and polygon are not naturally associated at the Element level.
        # the polygon is naturally aware of the vertices, but not necessarily of the Elements representing them, which is needed for the analysis done in this script.
        self.poly_to_vertices: Dict[Element, List[Element]] = {}

        self.all_segments: Dict[gt.Segment, bool] = {}

    def init_identifier_pool(self):
        self.identifier_pool = [chr(i) for i in range(65, 91)]  # A-Z
        self.secondary_identifier_pool = [f"{chr(i)}{j}" for i in range(65, 91) for j in range(1, 10)]  # A1-Z9
        
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

    def _get_unused_identifier(self, return_sequential: int = 0) -> str:
        """Get an unused identifier from the pool."""
        id_pool = self.identifier_pool if self.identifier_pool and len(self.identifier_pool) > return_sequential else self.secondary_identifier_pool
        if return_sequential > 0 and len(id_pool) > return_sequential:
            identifier = id_pool.pop(0) # the next time we call this function, we will, by construction, get the next index
        else:
            idx = random.randrange(len(id_pool))
            identifier = id_pool.pop(idx)
        return identifier

    # Identifiers assigned in this specific way are not automatically removed from the identifier pool,
    # so user needs to make sure to do so themselves.
    def _assign_specific_identifiers(self) -> str:
        if self.identifier_queue:
            return self.identifier_queue.pop(0)
        else:
            print("This wasn't supposed to happen. Ran out of identifiers to assign intentionally; user should have specified a longer queue before trying to call this function.")
            return self._get_unused_identifier(return_sequential=0)

    def _is_compatible_type(self, value_type, required_type) -> bool:
        return value_type == required_type or required_type == Any

    def _find_compatible_elements(self, required_type, angle_biases: Optional[List[float]] = None) -> List[Element]:
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
        if required_type == gt.AngleSize:
            # construct a new AngleSize
            if angle_biases is None:
                angle = random.choice(np.pi / 12 * np.arange(1, 13))
            else:
                angle = random.choice(angle_biases)
            element, const_command = self._add_constant('AngleSize', angle)
            return [element]
                
        # If this is a numeric type (int or float)
        if numeric_type is not None:            
            # Create a new constant with a random value
            if compatible and random.random() < 0.2: # make a new const with the same value; maybe it'll be interesting
                value = random.choice(compatible).data
            else:
                value = random.randint(1, 12)
            element, const_command = self._add_constant('int', value)
            # Return the newly created element
            return [element]
        
        return compatible
    
    def _update_dependency_graph(self, command: Command) -> None:
        if not self.dependency_graph:
            return
        input_elements = command.input_elements
        output_elements = command.output_elements
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
        elif const_type == 'AngleSize':
            data = AngleSize(value)
        const_command = ConstCommand(type(data), value, element)        
        
        const_command.apply()
        self.command_sequence.append(const_command)
        
        # Add to dependency graph
        if self.dependency_graph:
            self.dependency_graph.add_node(element, const_command)
            self.dependency_graph.add_dependency(element, [], const_command)
            
        return element, const_command

    def _try_apply_command(self, cmd_name: str, input_elements: List[Element], label_factory: Callable[[], str] = None) -> Tuple[bool, Command]:
        """
        Try to execute a command and return its result.
        
        Args:
            cmd_name: Name of the command to execute
            input_elements: List of Element objects containing the input data
            
        Returns:
            Tuple of (success, command):
            - success: Boolean indicating if the command executed successfully
            - command: The Command object that was executed
        """
        if label_factory is None:
            label_factory = self._get_unused_identifier
        try:
            if cmd_name == 'segment_pp' or cmd_name == 'diagonal_p':
                if (input_elements[0], input_elements[1]) in self.all_segments:
                    return False, None
            command = Command(cmd_name, input_elements, label_factory=label_factory, label_dict=self.identifiers)
            command.apply()

            if 'rotate_polygon' in cmd_name or cmd_name == 'polygon_from_center_and_circumradius':
                self.poly_to_vertices[command.output_elements[-1]] = command.output_elements[:-1]
            if cmd_name == 'diagonal_p' or cmd_name == 'segment_pp':
                self.all_segments[(command.input_elements[0], command.input_elements[1])] = True
                self.all_segments[(command.input_elements[1], command.input_elements[0])] = True
            return True, command
        except Exception as e:
            return False, None

    def _sample_commands(self) -> Generator[str, None, None]:
        # Shuffle commands to try
        command_names = list(self.available_commands.keys())
        if not self.made_triangle_already and "triangle_ppp" in command_names:
            command_names.append('triangle_ppp') # double the probability of triangle construction
        random.shuffle(command_names)
        


        for cmd_name in command_names:
            if 'prove' in cmd_name or 'measure' in cmd_name:
                continue # these are special commands, not part of constructions
            # heuristics for not making boring things
            # also minus and power make bad (ambiguous or dependent on calculation precision) problems
            if 'minus' in cmd_name:
                continue
            if 'sum' in cmd_name:
                continue
            if 'ratio' in cmd_name:
                continue
            if 'product' in cmd_name:
                continue
            if 'power_' in cmd_name:
                continue

            # this one is boring, since if you get a number out of something, you can't get anything more useful out of it, and if have have a polygon, you always have its circumradius, so you always have its area.
            if cmd_name == 'area_P':
                continue

            
            cmd_info = self.available_commands[cmd_name]
            if cmd_info['return_type'] == gt.Boolean:
                continue
            # decrease frequency of polygons
            if cmd_name == 'polygon_from_center_and_circumradius':
                # make sure they only happen near the beginning of the sequence, which is more natural
                if len(self.command_sequence) > 3:
                    continue
                # eliminate duplicates
                if self.made_polygon_already:
                    continue
                # still there are too many
                if random.random() < 0.5:
                    continue
        
            yield cmd_name

    def _sample_polygon_sides(self) -> int:
        sides = [4, 5, 6, 7, 8, 9, 10, 11, 12]
        weights = [1, 2, 4, 1, 4, 1, 2, 1, 4]
        return random.choices(sides, weights)[0]

    def _execute_new_command(self) -> Command:
        """
        Sample a random command that can be executed with existing elements.
        Returns a tuple of (input_elements, command) or None if no valid command can be sampled.
        """
        for cmd_name in self._sample_commands():
            cmd_info = self.available_commands[cmd_name]
            param_types = cmd_info['param_types']

            # Special case for point_ with no parameters
            # note: not sure this was necessary. i think other param logic is generic enough for this
            if cmd_name == 'point_' and len(param_types) == 0:
                # Try to execute the command directly
                success, command = self._try_apply_command(cmd_name, [])
                if success:
                    return command
                else:
                    continue
            num_points = len([x for x in self.identifiers.values() if isinstance(x.data, gt.Point)])
            if cmd_name == 'triangle_ppp':
                if (num_points <= 2):
                    success, command = self._try_apply_command('point_', [])
                    if success:
                        return command
                    else:
                        continue
                else:
                    self.made_triangle_already = True

            # Skip commands that need parameters if we don't have any elements yet
            if not self.identifiers and param_types and not all(t in (int, float) for t in param_types):
                continue
            
            # Try to find compatible parameters for the sampled command, ensuring they are unique
            valid_params = True
            if cmd_name == 'diagonal_p':
                # special semantics for this command, kind of a hack
                # simply sample two points and construct a segment, 
                # but these two points have to be vertices of a polygon.
                compatible = self._find_compatible_elements(gt.Polygon)
                if not compatible:
                    continue
                polygon_element: Element = random.choice(compatible)
                n = len(polygon_element.data.points)
                while True:
                    i, j = random.sample(range(n), 2)
                    if abs(i - j) % n != 1 and abs(i - j) % n != n - 1:
                        break
                # no need to construct the points, since they were already constructed
                # as vertices of the polygon
                points = self.poly_to_vertices[polygon_element]
                input_elements = [points[i], points[j]]
            else:
                input_elements = []
                used_elements = set()  # Track used elements to ensure uniqueness
                
                for param_type in param_types:
                    angle_biases = None
                    if cmd_name == 'rotate_polygon_about_center' and param_type == gt.AngleSize:
                        num_sides = len(input_elements[0].data.points)
                        angle_biases = [np.pi / num_sides * i for i in range(1, num_sides)] # rotate by multiples of one-half internal angle
                    compatible = self._find_compatible_elements(param_type, angle_biases)
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
                    used_elements.add(selected)
            if valid_params:
                if cmd_name == 'polygon_from_center_and_circumradius':
                    num_sides = self._sample_polygon_sides()
                    element, _ = self._add_constant('int', num_sides)
                    input_elements[0] = element
                # Try to execute the command
                success, command = self._try_apply_command(cmd_name, input_elements)
                if success:
                    return command
                else:
                    continue
        # we should never get here
        raise Exception("Somehow ran out of commands???")

    def generate_construction(self, num_commands: int = 5) -> List[Command]:
        """Generate a sequence of commands to form a valid construction."""
        # Start with a point, since that's usually necessary
        success, command = self._try_apply_command('point_', [])
        self.command_sequence.append(command)
        self._update_dependency_graph(command)

        while len(self.command_sequence) < num_commands:
            # Sample a command that can be executed
            command = self._execute_new_command()
            if command is None: # should not actually happen
                continue
            self.command_sequence.append(command)
            self._update_dependency_graph(command)
        
        return self.command_sequence

    def compute_longest_construction(self, j):
        """
        Find the measurable quantity with the most ancestors and create a pruned
        construction sequence that includes only the commands needed to construct it.
        """
            
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
        self._update_dependency_graph(measure_command)
        ordered_commands.append(measure_command)        



        # reassign identifiers starting from the beginning of the ident pool (shuffled, but with single char idents first),
        # so that the output is more readable
        # a funny thing happened here:
        # you don't have to rename the input elements, because the semantics of the rest of this program involve manipulating actual element objects.
        # so when you rename the output elements, you will rename every element which is actually used in the command sequence,
        # and the element object will be updated, passed around, and have the correct label when it is used as an input element.
        # in fact, trying to rename the input element will fail, because it has already been renamed.
        self.init_identifier_pool() # this effectively destroys all ability to assign idents later, so we have to be sure that this is one of the last things we ever do with this generator.
        for command in ordered_commands:
            if isinstance(command, ConstCommand):
                command.element.label = self._get_unused_identifier()
                continue
            if command.name == 'polygon_from_center_and_circumradius':
                num_sides = command.input_elements[0].data
                for i in range(num_sides):
                    output_elem = command.output_elements[i]
                    output_elem.label = self._get_unused_identifier(return_sequential=num_sides - i)
                command.output_elements[-1].label = self._get_unused_identifier() # the polygon itself
            elif command.name == 'rotate_polygon_about_center':
                for idx, output_elem in enumerate(command.output_elements[:-1]):
                    input_vertex = self.poly_to_vertices[command.input_elements[0]][idx]
                    output_elem.label = input_vertex.label + "'"
                command.output_elements[-1].label = command.input_elements[0].label + "'"
            else:
                for output_elem in command.output_elements:
                    output_elem.label = self._get_unused_identifier()

        self.pruned_command_sequence = ordered_commands
        return True

    def save_construction(self, filename: str, description: str = "Generated construction"):
        with open(filename, 'w') as f:
            f.write(f"# {description}\n")
            for cmd in self.pruned_command_sequence:
                f.write(f"{cmd}\n")


def write_construction(i, args):
    seed = args.seed + i if args.seed is not None else None
    generator_class = args.generator_class
    generator = generator_class(seed=seed, command_types=args.command_types)
    generator.generate_construction(num_commands=args.num_commands)
    
    # Prune the construction to include only essential commands
    success = generator.compute_longest_construction(i)
    if not success:
        return
    
    # Create unique filename if generating multiple constructions
    filename = os.path.join(args.output_dir, f"construction_{i+1}.txt")
        
    generator.save_construction(filename, f"Generated construction #{i+1}")

def parse_args():
    parser = argparse.ArgumentParser(description="Generate classical geometric constructions")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--num_commands", type=int, default=25, help="Number of commands to generate")
    parser.add_argument("--output_dir", type=str, default="generated_constructions/", help="Output directory")
    # note as a result of the multiprocessing, this is the number of construction attempts, not the number of constructions actually generated
    parser.add_argument("--count", type=int, default=20, help="Number of constructions to attempt")
    parser.add_argument("--max_workers", type=int, default=16, help="Maximum number of threads to use")
    parser.add_argument("--multiprocess", action="store_true", help="use multiprocessing")
    parser.add_argument("--command_types", type=str, nargs="+", choices=["polygon", "circle", "triangle", "basic", "angle", "all"], 
                        help="Types of geometric commands to include")
    # parser.add_argument("--generator", type=str, default="ClassicalGenerator", help="Generator to use")
    args = parser.parse_args()
    return args

def main(args):
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    if not args.multiprocess:
        for i in range(args.count):
            write_construction(i, args)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            futures = [executor.submit(write_construction, i, args) for i in range(args.count)]
            concurrent.futures.wait(futures)


if __name__ == "__main__":
    args = parse_args()
    args.generator_class = ClassicalGenerator
    main(args)
