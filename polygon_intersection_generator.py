from classical_generator import ClassicalGenerator
import random
import geo_types as gt
from typing import List, Union
import pdb
class PolygonInternalIntersectionGenerator(ClassicalGenerator):
    def __init__(self, seed=None):
        super().__init__(seed)
        self.point_count = 1 # since in generate_construction, we start with one point outside the loop
        self.polygon_created = False
        self.vertices = []
        self.segments_created = []
        
    def _sample_command(self):
        # First, create two points
        if self.point_count < 2:
            self.point_count += 1
            return 'point_', [], gt.Point
        
        # Then create a polygon with 6-12 sides using polygon_ppi
        elif not self.polygon_created:
            self.polygon_created = True
            # Get all point identifiers that we've created
            point_identifiers = [key for key in self.identifiers.keys()] # the first point, created in generate_construction
            for identifier, value_info in self.identifiers.items():
                if self._is_compatible_type(value_info['type'], gt.Point):
                    point_identifiers.append(identifier)
            
            p1, p2 = point_identifiers[:2]
            num_sides = random.randint(6, 12)
            num_sides_identifier = self._add_constant('int', num_sides)
            
            self.vertices = point_identifiers[:2]

            return 'polygon_ppi', [p1, p2, num_sides_identifier], List[Union[gt.Polygon, gt.Segment, gt.Point]]
        
        # After polygon creation, we need to update our vertex list
        elif len(self.vertices) <= 2:
            # Find all points in the identifiers dictionary
            all_points = []
            for identifier, value_info in self.identifiers.items():
                if self._is_compatible_type(value_info['type'], gt.Point):
                    all_points.append(identifier)
            
            # The polygon_ppi function creates additional points
            # The first two points are the ones we provided, and the rest are new vertices
            self.vertices = all_points
            pdb.set_trace()
            # Now we can create a segment between non-adjacent vertices
            return self._create_segment()
        
        # Create segments between non-adjacent vertices
        else:
            return self._create_segment()
    
    def _create_segment(self):
        # Choose two non-adjacent vertices
        valid_pairs = []
        for i, v1 in enumerate(self.vertices):
            for j, v2 in enumerate(self.vertices):
                if i != j:  # Don't create segment to self
                    # Check if vertices are non-adjacent in the polygon
                    # For a cycle, vertices i and j are adjacent if |i-j| = 1 or |i-j| = n-1 (connecting first and last)
                    dist = abs(i - j)
                    is_adjacent = (dist == 1 or dist == len(self.vertices) - 1)
                    pair_already_created = (v1, v2) in self.segments_created or (v2, v1) in self.segments_created
                    
                    if not is_adjacent and not pair_already_created:
                        valid_pairs.append((v1, v2))
        
        # Choose a random pair of non-adjacent vertices
        v1, v2 = random.choice(valid_pairs)
        self.segments_created.append((v1, v2))
        
        # Create a segment between these vertices
        return 'segment_pp', [v1, v2], gt.Segment
        

