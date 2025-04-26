import random
from classical_generator import ClassicalGenerator
import geo_types as gt
# this one is constrained to generate problems which at some point involve constructing a polygon, 
# and at one point rotating it around its center.
# later in the pipeline, the generated problem when translated into NL will have a different form:
# the "answer" to the measure will be given, and the new question will be to find the angle of rotation, which will be omitted.
class PolygonRotationGenerator(ClassicalGenerator):
    def __init__(self, seed=None):
        super().__init__(seed)
        self.made_polygon_already: bool = False
        self.rotated_polygon_already: bool = False
    # override 
    def _sample_command(self):
        if not self.made_polygon_already:
            self.made_polygon_already = True
            yield "polygon_from_center_and_circumradius" # note: this doesn't work,  you have to construct the args first... try yielding those above and setting true after; check resulting files

        command_names = list(self.available_commands.keys())
        if not self.rotated_polygon_already:
            command_names.append('rotate_polygon_about_center')
            command_names.append('rotate_polygon_about_center')
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

            
            cmd_info = self.available_commands[cmd_name]
            if cmd_info['return_type'] == gt.Boolean:
                continue
            # discourage multiple polygons
            if self.made_polygon_already and cmd_name == 'polygon_from_center_and_circumradius':
                if random.random() < 0.8:
                    continue
            # discourage multiple rotations
            if self.rotated_polygon_already and cmd_name == 'rotate_polygon_about_center':
                if random.random() < 0.8:
                    continue
            if cmd_name == 'rotate_polygon_about_center':
                self.rotated_polygon_already = True