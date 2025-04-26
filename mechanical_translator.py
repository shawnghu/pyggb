import math
import os
import argparse
import glob
from typing import List, Optional, Dict
from pathlib import Path
import pdb
import time
import hashlib
import time
import json
import concurrent.futures
import threading
import random  # Add this import for random selection
from dataclasses import dataclass
from geo_types import AngleSize
global_timestamp = str(int(time.time()))
# Add a file lock for thread-safe writing
file_lock = threading.Lock()

def invert_pi_expression(value):
    if isinstance(value, AngleSize):
        value = value.x
    if isinstance(value, str):
        value = float(value)
    if abs(value - math.pi) < 1e-4:
        return "pi"
    elif abs(value - math.pi / 2) < 1e-4:
        return "pi/2"
    elif abs(value - math.pi / 3) < 1e-4:
        return "pi/3"
    elif abs(value - 2 * math.pi / 3) < 1e-4:
        return "2pi/3"
    elif abs(value - math.pi / 4) < 1e-4:
        return "pi/4"
    elif abs(value - 3 * math.pi / 4) < 1e-4:
        return "3pi/4"
    elif abs(value - math.pi / 5) < 1e-4:
        return "pi/5"
    elif abs(value - 2 * math.pi / 5) < 1e-4:
        return "2pi/5"
    elif abs(value - 3 * math.pi / 5) < 1e-4:
        return "3pi/5"
    elif abs(value - 4 * math.pi / 5) < 1e-4:
        return "4pi/5"
    elif abs(value - math.pi / 6) < 1e-4:
        return "pi/6"
    elif abs(value - 5 * math.pi / 6) < 1e-4:
        return "5pi/6"
    elif abs(value - math.pi / 7) < 1e-4:
        return "pi/7"
    elif abs(value - 2 * math.pi / 7) < 1e-4:
        return "2pi/7"
    elif abs(value - 3 * math.pi / 7) < 1e-4:
        return "3pi/7"
    elif abs(value - 4 * math.pi / 7) < 1e-4:
        return "4pi/7"
    elif abs(value - 5 * math.pi / 7) < 1e-4:
        return "5pi/7"
    elif abs(value - 6 * math.pi / 7) < 1e-4:
        return "6pi/7"
    elif abs(value - math.pi / 8) < 1e-4:
        return "pi/8"
    elif abs(value - 3 * math.pi / 8) < 1e-4:
        return "3pi/8"
    elif abs(value - 5 * math.pi / 8) < 1e-4:
        return "5pi/8"
    elif abs(value - 7 * math.pi / 8) < 1e-4:
        return "7pi/8"
    elif abs(value - math.pi / 9) < 1e-4:
        return "pi/9"
    elif abs(value - 2 * math.pi / 9) < 1e-4:
        return "2pi/9"
    elif abs(value - 4 * math.pi / 9) < 1e-4:
        return "4pi/9"
    elif abs(value - 5 * math.pi / 9) < 1e-4:
        return "5pi/9"
    elif abs(value - 7 * math.pi / 9) < 1e-4:
        return "7pi/9"
    elif abs(value - 8 * math.pi / 9) < 1e-4:
        return "8pi/9"
    elif abs(value - math.pi / 10) < 1e-4:
        return "pi/10"
    elif abs(value - 3 * math.pi / 10) < 1e-4:
        return "3pi/10"
    elif abs(value - 7 * math.pi / 10) < 1e-4:
        return "7pi/10"
    elif abs(value - 9 * math.pi / 10) < 1e-4:
        return "9pi/10"
    elif abs(value - math.pi / 11) < 1e-4:
        return "pi/11"
    elif abs(value - 2 * math.pi / 11) < 1e-4:
        return "2pi/11"
    elif abs(value - 3 * math.pi / 11) < 1e-4:
        return "3pi/11"
    elif abs(value - 4 * math.pi / 11) < 1e-4:
        return "4pi/11"
    elif abs(value - 5 * math.pi / 11) < 1e-4:
        return "5pi/11"
    elif abs(value - 6 * math.pi / 11) < 1e-4:
        return "6pi/11"
    elif abs(value - 7 * math.pi / 11) < 1e-4:
        return "7pi/11"
    elif abs(value - 8 * math.pi / 11) < 1e-4:
        return "8pi/11"
    elif abs(value - 9 * math.pi / 11) < 1e-4:
        return "9pi/11"
    elif abs(value - 10 * math.pi / 11) < 1e-4:
        return "10pi/11"
    elif abs(value - math.pi / 12) < 1e-4:
        return "pi/12"
    elif abs(value - 5 * math.pi / 12) < 1e-4:
        return "5pi/12"
    elif abs(value - 7 * math.pi / 12) < 1e-4:
        return "7pi/12"
    elif abs(value - 11 * math.pi / 12) < 1e-4:
        return "11pi/12"
    else:
        return str(value)


@dataclass
class Command:
    name: str
    inputs: tuple[str]
    output: Optional[str] = None



def translate_problem(contents: str) -> Optional[str]:
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
        "point_": [
            "Construct a point {0}.",
            "Place a point {0}.",
            "Mark a point {0}.",
            "Create a point {0}.",
            "Position a point {0}."
        ],
        "point_c": [
            "Construct a point {0} on circle {1}.",
            "Place a point {0} anywhere on circle {1}.",
            "Mark a point {0} on the circumference of circle {1}.",
            "Create a point {0} that lies on circle {1}.",
            "Position a point {0} somewhere on circle {1}."
        ],
        "point_l": [
            "Construct a point {0} on line {1}.",
            "Place a point {0} anywhere on line {1}.",
            "Mark a point {0} that lies on line {1}.",
            "Create a point {0} situated on line {1}.",
            "Position a point {0} at any location on line {1}."
        ],
        "point_s": [
            "Construct a point {0} on segment {1}.",
            "Place a point {0} anywhere on segment {1}.",
            "Mark a point {0} that lies on segment {1}.",
            "Create a point {0} situated on segment {1}.",
            "Position a point {0} at any location on segment {1}."
        ],
        "point_pm": [
            "Construct a point {0} at distance {2} from point {1}.",
            "Place a point {0} that is {2} units away from point {1}.",
            "Mark a point {0} such that its distance from point {1} is {2}.",
            "Create a point {0} at a distance of {2} from point {1}.",
            "Position a point {0} so that it is exactly {2} units from point {1}."
        ],
        "point_at_distance": [
            "Construct point {0} at distance {2} from point {1} in a random direction.",
            "Place point {0} so that it is {2} units away from point {1} in any direction.",
            "Mark point {0} at a distance of {2} from point {1} in an arbitrary direction.",
            "Create point {0} such that it lies {2} units from point {1} in any direction.",
            "Position point {0} at a distance of {2} from point {1}, in whichever direction you choose."
        ],
        "point_at_distance_along_line": [
            "Construct point {0} on line {1}, at distance {3} from point {2}.",
            "Place point {0} on line {1} such that it is {3} units away from point {2}.",
            "Mark point {0} on line {1} at a distance of {3} from point {2}.",
            "Create point {0} on line {1} so that its distance from point {2} is {3}.",
            "Position point {0} on line {1}, exactly {3} units away from point {2}."
        ],
        
        # Line creation
        "line_pp": [
            "Construct a line {0} through points {1} and {2}.",
            "Draw a line {0} that passes through points {1} and {2}.",
            "Create a line {0} connecting points {1} and {2}.",
            "Form a line {0} that goes through points {1} and {2}.",
            "Establish a line {0} passing through both points {1} and {2}."
        ],
        "line_pl": [
            "Construct a line {0} through point {1} parallel to line {2}.",
            "Draw a line {0} passing through point {1} that is parallel to line {2}.",
            "Create a line {0} through point {1} that never intersects line {2}.",
            "Form a line {0} through point {1} maintaining the same direction as line {2}.",
            "Establish a line {0} through point {1} that runs parallel to line {2}."
        ],
        "line_pr": [
            "Construct a line {0} through point {1} parallel to ray {2}.",
            "Draw a line {0} passing through point {1} that is parallel to ray {2}.",
            "Create a line {0} through point {1} that never intersects ray {2}.",
            "Form a line {0} through point {1} maintaining the same direction as ray {2}.",
            "Establish a line {0} through point {1} that runs parallel to ray {2}."
        ],
        "line_ps": [
            "Construct a line {0} through point {1} parallel to segment {2}.",
            "Draw a line {0} passing through point {1} that is parallel to segment {2}.",
            "Create a line {0} through point {1} that runs in the same direction as segment {2}.",
            "Form a line {0} through point {1} maintaining the same orientation as segment {2}.",
            "Establish a line {0} through point {1} that is parallel to segment {2}."
        ],
        "line_bisector_pp": [
            "Construct the perpendicular bisector {0} of points {1} and {2}.",
            "Draw the perpendicular bisector {0} of the line segment connecting points {1} and {2}.",
            "Create the line {0} that perpendicularly bisects the segment between points {1} and {2}.",
            "Form the perpendicular bisector {0} of the segment from point {1} to point {2}.",
            "Establish the line {0} that divides the segment between {1} and {2} into two equal parts and is perpendicular to it."
        ],
        "line_bisector_s": [
            "Construct the perpendicular bisector {0} of segment {1}.",
            "Draw the perpendicular bisector {0} that divides segment {1} into two equal parts.",
            "Create the line {0} that perpendicularly bisects segment {1}.",
            "Form the perpendicular bisector {0} that cuts segment {1} into two equal halves.",
            "Establish the line {0} that is perpendicular to segment {1} and passes through its midpoint."
        ],
        
        # Orthogonal lines
        "orthogonal_line_pl": [
            "Construct a line {0} through point {1} perpendicular to line {2}.",
            "Draw a line {0} passing through point {1} that is perpendicular to line {2}.",
            "Create a line {0} through point {1} that forms a right angle with line {2}.",
            "Form a line {0} through point {1} that is at a 90-degree angle to line {2}.",
            "Establish a line {0} through point {1} that is orthogonal to line {2}."
        ],
        "orthogonal_line_pr": [
            "Construct a line {0} through point {1} perpendicular to ray {2}.",
            "Draw a line {0} passing through point {1} that is perpendicular to ray {2}.",
            "Create a line {0} through point {1} that forms a right angle with ray {2}.",
            "Form a line {0} through point {1} that is at a 90-degree angle to ray {2}.",
            "Establish a line {0} through point {1} that is orthogonal to ray {2}."
        ],
        "orthogonal_line_ps": [
            "Construct a line {0} through point {1} perpendicular to segment {2}.",
            "Draw a line {0} passing through point {1} that is perpendicular to segment {2}.",
            "Create a line {0} through point {1} that forms a right angle with segment {2}.",
            "Form a line {0} through point {1} that is at a 90-degree angle to segment {2}.",
            "Establish a line {0} through point {1} that is orthogonal to segment {2}."
        ],
        
        # Angular bisectors
        "angular_bisector_ll": [
            "Construct the angle bisectors {0}, {1} of lines {2} and {3}.",
            "Draw the angle bisectors {0}, {1} that divide the angles formed by lines {2} and {3}.",
            "Create the lines {0}, {1} that bisect the angles between lines {2} and {3}.",
            "Form the angle bisectors {0}, {1} for the angles created by lines {2} and {3}.",
            "Establish the lines {0}, {1} that divide the angles between lines {2} and {3} into equal parts."
        ],
        "angular_bisector_ppp": [
            "Construct the angle bisector {0} of angle {1}{2}{3}.",
            "Draw the angle bisector {0} that divides angle {1}{2}{3} into two equal parts.",
            "Create the line {0} that bisects the angle formed by points {1}, {2}, and {3}.",
            "Form the angle bisector {0} that splits angle {1}{2}{3} into two equal angles.",
            "Establish the ray {0} that divides angle {1}{2}{3} into two congruent angles."
        ],
        "angular_bisector_ss": [
            "Construct the angle bisectors {0}, {1} of segments {2} and {3}.",
            "Draw the angle bisectors {0}, {1} that divide the angles formed by segments {2} and {3}.",
            "Create the lines {0}, {1} that bisect the angles between segments {2} and {3}.",
            "Form the angle bisectors {0}, {1} for the angles created by segments {2} and {3}.",
            "Establish the lines {0}, {1} that divide the angles between segments {2} and {3} into equal parts."
        ],
        
        # Intersections
        "intersect_ll": [
            "Find the intersection point {0} of lines {1} and {2}.",
            "Determine the point {0} where lines {1} and {2} intersect.",
            "Locate the point {0} at which lines {1} and {2} cross each other.",
            "Identify the point {0} common to both lines {1} and {2}.",
            "Mark the point {0} where lines {1} and {2} meet."
        ],
        "intersect_lc": [
            "Find the intersection point {0} of line {1} and circle {2}.",
            "Determine the point {0} where line {1} intersects circle {2}.",
            "Locate the point {0} at which line {1} crosses circle {2}.",
            "Identify the point {0} common to both line {1} and circle {2}.",
            "Mark the point {0} where line {1} meets circle {2}."
        ],
        "intersect_cs": [
            "Find the intersection point {0} of circle {1} and segment {2}.",
            "Determine the point {0} where circle {1} intersects segment {2}.",
            "Locate the point {0} at which circle {1} crosses segment {2}.",
            "Identify the point {0} common to both circle {1} and segment {2}.",
            "Mark the point {0} where circle {1} meets segment {2}."
        ],
        "intersect_cc": [
            "Find the intersection point {0} of circles {1} and {2}.",
            "Determine the point {0} where circles {1} and {2} intersect.",
            "Locate the point {0} at which circles {1} and {2} cross each other.",
            "Identify the point {0} common to both circles {1} and {2}.",
            "Mark the point {0} where circles {1} and {2} meet."
        ],
        "intersect_cl": [
            "Find the intersection point {0} of circle {1} and line {2}.",
            "Determine the point {0} where circle {1} intersects line {2}.",
            "Locate the point {0} at which circle {1} crosses line {2}.",
            "Identify the point {0} common to both circle {1} and line {2}.",
            "Mark the point {0} where circle {1} meets line {2}."
        ],
        "intersect_lr": [
            "Find the intersection point {0} of line {1} and ray {2}.",
            "Determine the point {0} where line {1} intersects ray {2}.",
            "Locate the point {0} at which line {1} crosses ray {2}.",
            "Identify the point {0} common to both line {1} and ray {2}.",
            "Mark the point {0} where line {1} meets ray {2}."
        ],
        "intersect_ls": [
            "Find the intersection point {0} of line {1} and segment {2}.",
            "Determine the point {0} where line {1} intersects segment {2}.",
            "Locate the point {0} at which line {1} crosses segment {2}.",
            "Identify the point {0} common to both line {1} and segment {2}.",
            "Mark the point {0} where line {1} meets segment {2}."
        ],
        "intersect_rl": [
            "Find the intersection point {0} of ray {1} and line {2}.",
            "Determine the point {0} where ray {1} intersects line {2}.",
            "Locate the point {0} at which ray {1} crosses line {2}.",
            "Identify the point {0} common to both ray {1} and line {2}.",
            "Mark the point {0} where ray {1} meets line {2}."
        ],
        "intersect_rr": [
            "Find the intersection point {0} of rays {1} and {2}.",
            "Determine the point {0} where rays {1} and {2} intersect.",
            "Locate the point {0} at which rays {1} and {2} cross each other.",
            "Identify the point {0} common to both rays {1} and {2}.",
            "Mark the point {0} where rays {1} and {2} meet."
        ],
        "intersect_rs": [
            "Find the intersection point {0} of ray {1} and segment {2}.",
            "Determine the point {0} where ray {1} intersects segment {2}.",
            "Locate the point {0} at which ray {1} crosses segment {2}.",
            "Identify the point {0} common to both ray {1} and segment {2}.",
            "Mark the point {0} where ray {1} meets segment {2}."
        ],
        "intersect_sl": [
            "Find the intersection point {0} of segment {1} and line {2}.",
            "Determine the point {0} where segment {1} intersects line {2}.",
            "Locate the point {0} at which segment {1} crosses line {2}.",
            "Identify the point {0} common to both segment {1} and line {2}.",
            "Mark the point {0} where segment {1} meets line {2}."
        ],
        "intersect_sr": [
            "Find the intersection point {0} of segment {1} and ray {2}.",
            "Determine the point {0} where segment {1} intersects ray {2}.",
            "Locate the point {0} at which segment {1} crosses ray {2}.",
            "Identify the point {0} common to both segment {1} and ray {2}.",
            "Mark the point {0} where segment {1} meets ray {2}."
        ],
        "intersect_ss": [
            "Find the intersection point {0} of segments {1} and {2}.",
            "Determine the point {0} where segments {1} and {2} intersect.",
            "Locate the point {0} at which segments {1} and {2} cross each other.",
            "Identify the point {0} common to both segments {1} and {2}.",
            "Mark the point {0} where segments {1} and {2} meet."
        ],
        
        # Circles
        "circle_pp": [
            "Construct a circle {0} with center {1} passing through point {2}.",
            "Draw a circle {0} centered at {1} that passes through point {2}.",
            "Create a circle {0} with its center at {1} and containing point {2} on its circumference.",
            "Form a circle {0} centered at point {1} such that point {2} lies on it.",
            "Establish a circle {0} with center {1} and radius equal to the distance from {1} to {2}."
        ],
        "circle_ppp": [
            "Construct a circle {0} passing through points {1}, {2}, and {3}.",
            "Draw a circle {0} that passes through the three points {1}, {2}, and {3}.",
            "Create a circle {0} containing points {1}, {2}, and {3} on its circumference.",
            "Form a circle {0} such that points {1}, {2}, and {3} all lie on it.",
            "Establish a circle {0} that passes through each of the points {1}, {2}, and {3}."
        ],
        "circle_pm": [
            "Construct a circle {0} with center {1} and radius {2}.",
            "Draw a circle {0} centered at {1} with a radius of {2} units.",
            "Create a circle {0} with its center at point {1} and radius equal to {2}.",
            "Form a circle {0} centered at {1} with a distance of {2} from center to circumference.",
            "Establish a circle {0} with center point {1} and radius measuring {2} units."
        ],
        "circle_ps": [
            "Construct a circle {0} with center {1} and radius equal to the length of segment {2}.",
            "Draw a circle {0} centered at {1} with radius equal to the length of segment {2}.",
            "Create a circle {0} with its center at point {1} and radius matching the length of segment {2}.",
            "Form a circle {0} centered at {1} with a radius that equals the length of segment {2}.",
            "Establish a circle {0} with center point {1} and radius identical to the length of segment {2}."
        ],
        "center_c": [
            "Let {0} be the center of circle {1}.",
            "Mark point {0} as the center of circle {1}.",
            "Identify point {0} as the center point of circle {1}.",
            "Designate point {0} as the center of circle {1}.",
            "Define point {0} to be the center of circle {1}."
        ],
        
        # Segments
        "segment_pp": [
            "Construct segment {0} from point {1} to point {2}.",
            "Draw a line segment {0} connecting points {1} and {2}.",
            "Create a line segment {0} between points {1} and {2}.",
            "Form segment {0} joining points {1} and {2}.",
            "Establish a line segment {0} from point {1} to point {2}."
        ],
        
        # Midpoints
        "midpoint_pp": [
            "Find the midpoint {0} of points {1} and {2}.",
            "Locate the midpoint {0} between points {1} and {2}.",
            "Determine the point {0} that is equidistant from points {1} and {2}.",
            "Identify the midpoint {0} of the segment connecting points {1} and {2}.",
            "Mark the point {0} that divides the segment from {1} to {2} into two equal parts."
        ],
        "midpoint_s": [
            "Find the midpoint {0} of segment {1}.",
            "Locate the midpoint {0} of segment {1}.",
            "Determine the point {0} that divides segment {1} into two equal parts.",
            "Identify the point {0} at the middle of segment {1}.",
            "Mark the point {0} that is equidistant from both endpoints of segment {1}."
        ],
        
        # Reflections/Mirrors
        "mirror_pp": [
            "Reflect point {1} across point {2}, and call the resulting point {0}.",
            "Create point {0} as the reflection of point {1} across point {2}.",
            "Find point {0} such that point {2} is the midpoint of the segment from {1} to {0}.",
            "Determine point {0} by reflecting point {1} through point {2}.",
            "Construct point {0} as the image of point {1} when reflected over point {2}."
        ],
        "mirror_pl": [
            "Reflect point {1} across line {2}, and call the resulting point {0}.",
            "Create point {0} as the reflection of point {1} across line {2}.",
            "Find point {0} such that line {2} is the perpendicular bisector of segment from {1} to {0}.",
            "Determine point {0} by reflecting point {1} over line {2}.",
            "Construct point {0} as the image of point {1} when reflected across line {2}."
        ],
        "mirror_ps": [
            "Reflect point {1} across segment {2}, and call the resulting point {0}.",
            "Create point {0} as the reflection of point {1} across segment {2}.",
            "Find point {0} by reflecting point {1} over segment {2}.",
            "Determine point {0} as the mirror image of point {1} with segment {2} as the mirror.",
            "Construct point {0} as the image of point {1} when reflected across segment {2}."
        ],
        "mirror_pc": [
            "Invert point {1} with respect to circle {2}, and call the resulting point {0}.",
            "Create point {0} as the inversion of point {1} with respect to circle {2}.",
            "Find point {0} by inverting point {1} in circle {2}.",
            "Determine point {0} as the result of inverting point {1} with respect to circle {2}.",
            "Construct point {0} as the image of point {1} under inversion in circle {2}."
        ],
        "mirror_lp": [
            "Reflect line {1} across point {2}, and call the resulting line {0}.",
            "Create line {0} as the reflection of line {1} across point {2}.",
            "Find line {0} by reflecting line {1} through point {2}.",
            "Determine line {0} as the mirror image of line {1} with point {2} as the center of reflection.",
            "Construct line {0} as the image of line {1} when reflected over point {2}."
        ],
        "mirror_ll": [
            "Reflect line {1} across line {2}, and call the resulting line {0}.",
            "Create line {0} as the reflection of line {1} across line {2}.",
            "Find line {0} by reflecting line {1} over line {2}.",
            "Determine line {0} as the mirror image of line {1} with line {2} as the mirror.",
            "Construct line {0} as the image of line {1} when reflected across line {2}."
        ],
        "mirror_cl": [
            "Reflect circle {1} across line {2}, and call the resulting circle {0}.",
            "Create circle {0} as the reflection of circle {1} across line {2}.",
            "Find circle {0} by reflecting circle {1} over line {2}.",
            "Determine circle {0} as the mirror image of circle {1} with line {2} as the mirror.",
            "Construct circle {0} as the image of circle {1} when reflected across line {2}."
        ],
        "mirror_cp": [
            "Reflect circle {1} across point {2}, and call the resulting circle {0}.",
            "Create circle {0} as the reflection of circle {1} across point {2}.",
            "Find circle {0} by reflecting circle {1} through point {2}.",
            "Determine circle {0} as the mirror image of circle {1} with point {2} as the center of reflection.",
            "Construct circle {0} as the image of circle {1} when reflected over point {2}."
        ],
        
        # Angles
        "angle_ppp": [
            "Measure the angle {0} formed by points {1}, {2}, and {3}.",
            "Find the measure of angle {0} formed by points {1}, {2}, and {3}.",
            "Determine the angle {0} created by the three points {1}, {2}, and {3}.",
            "Calculate the measure of angle {0} with vertex at {2} and sides passing through {1} and {3}.",
            "Compute the angle {0} formed by the rays from point {2} to points {1} and {3}."
        ],
        
        # Measures
        "distance_pp": [
            "Measure the distance {0} between points {1} and {2}.",
            "Find the length {0} between points {1} and {2}.",
            "Determine the distance {0} from point {1} to point {2}.",
            "Compute the length {0} of the straight line from point {1} to point {2}."
        ],
        "radius_c": [
            "Measure the radius {0} of circle {1}.",
            "Find the radius {0} of circle {1}.",
            "Determine the radius {0} of circle {1}.",
            "Compute the value {0} equal to the radius of circle {1}."
        ],
        "area_P": [
            "Calculate the area {0} of polygon {1}.",
            "Determine the area {0} of polygon {1}.",
            "Find the area {0} enclosed by polygon {1}.",
        ],
        
        # Ray
        "ray_pp": [
            "Construct ray {0} starting at point {1} and passing through point {2}.",
            "Draw ray {0} with endpoint at {1} that passes through point {2}.",
            "Create ray {0} originating from point {1} and extending through point {2}.",
            "Form ray {0} with its vertex at {1} and passing through point {2}.",
        ],
        
        # Rotations
        "rotate_pap": [
            "Rotate point {1} by the measure of angle {2} around point {3}, and call the resulting point {0}.",
            "Create point {0} by rotating point {1} by the measure of angle {2} around point {3}.",
            "Find point {0} by rotating point {1} through the measure of angle {2} with center of rotation at {3}.",
            "Determine point {0} as the image of point {1} when rotated by the measure of angle {2} about point {3}.",
            "Construct point {0} by turning point {1} through the measure of angle {2} around the fixed point {3}."
        ],
        "rotate_pAp": [
            "Rotate point {1} by an angle of {2} radians around point {3}, and call the resulting point {0}.",
            "Create point {0} by rotating point {1} by an angle of {2} radians around point {3}.",
            "Find point {0} by rotating point {1} through an angle of {2} radians with center of rotation at {3}.",
            "Determine point {0} as the image of point {1} when rotated by an angle of {2} radians about point {3}.",
            "Construct point {0} by turning point {1} through an angle of {2} radians around the fixed point {3}."
        ],
        
        # Vectors
        "vector_pp": [
            "Construct vector {0} from point {1} to point {2}.",
            "Create vector {0} directed from point {1} to point {2}.",
            "Define vector {0} starting at point {1} and ending at point {2}.",
            "Form vector {0} with initial point {1} and terminal point {2}.",
            "Establish vector {0} pointing from point {1} toward point {2}."
        ],
        "translate_pv": [
            "Translate point {1} by vector {2}, and call the resulting point {0}.",
            "Create point {0} by translating point {1} along vector {2}.",
            "Find point {0} by moving point {1} according to vector {2}.",
            "Determine point {0} as the image of point {1} when translated by vector {2}.",
            "Construct point {0} by shifting point {1} in the direction and magnitude of vector {2}."
        ],
        # Tangents
        "tangent_pc": [
            "Construct the tangent line {0} from point {1} to circle {2}.",
            "Draw the tangent line {0} that passes through point {1} and touches circle {2}.",
            "Create the line {0} passing through point {1} that is tangent to circle {2}.",
            "Form the tangent line {0} from point {1} to circle {2}.",
            "Establish the line {0} through point {1} that touches circle {2} at exactly one point."
        ],
        "polar_pc": [
            "Construct the polar line {0} of point {1} with respect to circle {2}.",
            "Draw the polar line {0} of point {1} with respect to circle {2}.",
            "Create the polar line {0} of point {1} relative to circle {2}.",
            "Form the polar line {0} corresponding to point {1} with respect to circle {2}.",
            "Establish the polar line {0} of point {1} in relation to circle {2}."
        ],
        
        # Triangle-related commands
        "triangle_ppp": [
            "Construct triangle {0} with vertices at points {1}, {2}, and {3}.",
            "Draw triangle {0} using points {1}, {2}, and {3} as vertices.",
            "Create triangle {0} whose vertices are points {1}, {2}, and {3}."
        ],
        "circumcircle_t": [
            "Construct the circumcircle {0} of triangle {1}.",
            "Draw the circle {0} that passes through all three vertices of triangle {1}.",
            "Create the circumscribed circle {0} of triangle {1}."
        ],
        "circumcenter_t": [
            "Find the circumcenter {0} of triangle {1}.",
            "Locate the point {0} that is the center of the circumscribed circle of triangle {1}.",
            "Determine the circumcenter {0} of triangle {1}, which is equidistant from all three vertices."
        ],
        "circumradius_t": [
            "Measure the circumradius {0} of triangle {1}.",
            "Find the length {0} of the radius of the circumscribed circle of triangle {1}.",
            "Determine the circumradius {0} of triangle {1}, which is the distance from its circumcenter to any vertex."
        ],
        "centroid_t": [
            "Find the centroid {0} of triangle {1}.",
            "Locate the point {0} that is the centroid of triangle {1}.",
            "Determine the point {0} where the three medians of triangle {1} intersect."
        ],
        "incircle_t": [
            "Construct the incircle {0} of triangle {1}.",
            "Draw the circle {0} that is tangent to all three sides of triangle {1}.",
            "Create the inscribed circle {0} of triangle {1}."
        ],
        "incenter_t": [
            "Let {0} be the incenter of triangle {1}.",
            "Locate the point {0} that is the center of the inscribed circle of triangle {1}.",
            "Determine the incenter {0} of triangle {1}."
        ],
        "inradius_t": [
            "Measure the inradius {0} of triangle {1}.",
            "Find the length {0} of the radius of the inscribed circle of triangle {1}.",
            "Determine the inradius {0} of triangle {1}."
        ],
        "orthocenter_t": [
            "Find the orthocenter {0} of triangle {1}.",
            "Locate the point {0} where the three altitudes of triangle {1} intersect.",
            "Determine the orthocenter {0} of triangle {1}, the point where its three altitudes meet."
        ],

        # odd duck
        "circumcircle_p": [
            "Construct the circumcircle {0} of polygon {1}.",
            "Draw the circle {0} that passes through all the vertices of polygon {1}.",
            "Create the circumcircle {0} of polygon {1}."
        ],
    }
    stats = {
        "num_commands": 0,
        "measure_type": "other",
        "num_raw_points_constructed": 0,
        "num_lines_constructed": 0,
        "num_circles_constructed": 0,
        "num_angles_constructed": 0,
        "num_segments_constructed": 0,
        "num_triangles_constructed": 0,
        "num_polygons_constructed": 0,
        "num_midpoints_constructed": 0,
        "num_rotations": 0,
        "num_reflections": 0,
        "num_intersections": 0, 
        "num_angle_bisections": 0,
        "num_special_triangle_ops": 0,
    }
    num_commands = 0
    # Initialize the result list
    result_lines = []
    command_constructed_by = {}
    # Some things, such as consts, phrases like "angle ABC" or "circle ABC" or "segment AB" should be referred to as such and not given a new identifier in natural language.
    idents = {}
    # Process each line
    for line in contents.strip().split('\n'):
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue

        # this has to go at the very beginning because const command syntax is different from every other: contains no ':'
        if "const" in line:
            output = line.strip().split(' ')[-1]
            value = line.strip().split(' ')[2]
            idents[output] = value
        
        num_commands += 1

        # Split the line into command and arguments
        parts = line.split(':')
        if len(parts) < 2:
            continue
            
        cmd = parts[0].strip()

        
        # Split arguments into inputs and outputs
        args_parts = parts[1].split('->')
        if len(args_parts) < 2:
            continue
        
        # gather construction stats here, so it's all in one place
        if "point" in cmd:
            stats["num_raw_points_constructed"] += 1 # including point_at_distance*, not including intersection points
        if "circle" in cmd: # including incircle, circumcircle
            stats["num_circles_constructed"] += 1
        if "polygon" in cmd: # including rotate_polygon_about_center
            stats["num_polygons_constructed"] += 1
        if ("line" in cmd and "bisector" not in cmd) or "polar_pc" in cmd or "tangent_pc" in cmd: # this includes orthogonal lines, but not angle_bisector
            stats["num_lines_constructed"] += 1
        if "segment" in cmd or "diagonal_p" in cmd:
            stats["num_segments_constructed"] += 1
        if "angle" in cmd:
            stats["num_angles_constructed"] += 1
        if "intersect" in cmd:
            stats["num_intersections"] += 1
        if "mirror" in cmd:
            stats["num_reflections"] += 1
        if "midpoint" in cmd or "line_bisector" in cmd:
            stats["num_midpoints_constructed"] += 1
        if "rotate" in cmd: # including rotate_polygon_about_center
            stats["num_rotations"] += 1
        if "angular_bisector" in cmd:
            stats["num_angle_bisections"] += 1
        if "triangle" in cmd:
            stats["num_triangles_constructed"] += 1
        if cmd.endswith("_t"):
            stats["num_special_triangle_ops"] += 1
            
            
            

        raw_inputs = [arg.strip() for arg in args_parts[0].split() if arg.strip()]
        outputs = [arg.strip() for arg in args_parts[1].split() if arg.strip()]
        inputs = [idents[arg] if arg in idents else arg for arg in raw_inputs]
        for output in outputs:
            command_constructed_by[output] = Command(cmd, inputs)
        

        if cmd == "segment_pp":
            idents[outputs[0]] = inputs[0] + inputs[1]
            continue
        if cmd == "angle_ppp":
            idents[outputs[0]] = inputs[0] + inputs[1] + inputs[2]
            continue
        if cmd == "triangle_ppp":
            idents[outputs[0]] = inputs[0] + inputs[1] + inputs[2]
            continue
        if cmd == "diagonal_p":
            idents[outputs[0]] = "diagonal " + inputs[0] + inputs[1]
            '''
            line_templates = [
                f"Construct the diagonal {inputs[0]}{inputs[1]}.",
                f"Draw the diagonal from {inputs[0]} to {inputs[1]}.",
                f"Create the diagonal {inputs[0]}{inputs[1]}."
            ]
            translated_line = random.choice(line_templates)
            result_lines.append(translated_line)
            '''
            continue
        
        if cmd == "polygon_ppi":
            num_sides = int(inputs[-1])
            if num_sides <= 3:
                return None, None
            polygon_name = outputs[0]
            polygon_segment_idents = outputs[1:1+num_sides]
            polygon_vertex_idents = inputs[0:2] + outputs[1+num_sides:]

            for idx, segment_ident in enumerate(polygon_segment_idents):
                idents[segment_ident] = "segment " + polygon_vertex_idents[idx] + polygon_vertex_idents[(idx+1) % num_sides]
                
            # Provide two alternative phrasings for polygon construction
            polygon_templates = [
                f"Construct a regular polygon with {num_sides} sides starting from points {inputs[0]} and {inputs[1]}. Call the new vertices, in counterclockwise order after {inputs[1]}, {polygon_vertex_idents[2:]}, and label the resulting polygon as {polygon_name}.",
                f"Create a regular {num_sides}-sided polygon beginning at points {inputs[0]} and {inputs[1]}. Name the additional vertices, in counterclockwise order after {inputs[1]}, {polygon_vertex_idents[2:]}, and denote the polygon as {polygon_name}.",
                f"Create a regular {num_sides}-sided polygon where the vertices in counterclockwise order are {inputs[0]}, {inputs[1]} and the {num_sides - 2} new vertices {polygon_vertex_idents[2:]}; denote the polygon itself {polygon_name}.",
            ]
            translated_line = random.choice(polygon_templates)
            result_lines.append(translated_line)
            continue

        if cmd == "polygon_from_center_and_circumradius":
            polygon_templates = [
                f"Construct a regular polygon with {inputs[0]} sides, centered at {inputs[1]} with a circumradius of {inputs[2]}. Call the resulting polygon {outputs[-1]}, and its vertices (in counterclockwise order) {outputs[:-1]}.",
                f"Create a regular {inputs[0]}-sided polygon with center at point {inputs[1]} and circumradius equal to {inputs[2]}. Label this polygon as {outputs[-1]}, and its vertices (in counterclockwise order) {outputs[:-1]}.",
                f"Draw a regular polygon having {inputs[0]} sides, with its center at {inputs[1]} and distance {inputs[2]} from center to any vertex. Name this polygon {outputs[-1]}, and its vertices (in counterclockwise order) {outputs[:-1]}."
            ]
            translated_line = random.choice(polygon_templates)
            result_lines.append(translated_line)
            continue

        if cmd == "rotate_polygon_about_center_by_equivalent_angle":
            polygon_templates = [
                f"Rotate the polygon {inputs[0]} about its center counterclockwise by an angle equivalent to the measure of angle {inputs[1]}. Call the resulting polygon {outputs[-1]}, and the corresponding vertices {outputs[:-1]}.",
                f"Create the polygon {outputs[-1]} by rotating the polygon {inputs[0]} counterclockwise  about its center by the same angle as the measure of angle {inputs[1]}. Label the vertices of the resulting polygon {outputs[:-1]}, in correspondence to the vertices of {inputs[0]}.",
                f"Draw the polygon {outputs[-1]} by rotating {inputs[0]} counterclockwise about its center by an angle equal to the measure of angle {inputs[1]}. Label the vertices of the resulting polygon {outputs[:-1]}, in correspondence to the vertices of {inputs[0]}."
            ]
            translated_line = random.choice(polygon_templates)
            result_lines.append(translated_line)
            continue

        if cmd == "rotate_polygon_about_center":
            polygon_templates = [
                f"Rotate the polygon {inputs[0]} about its center counterclockwise by an angle of {invert_pi_expression(inputs[1])} radians. Call the resulting polygon {outputs[-1]}, and the corresponding vertices {outputs[:-1]}.",
                f"Create the polygon {outputs[-1]} by rotating the polygon {inputs[0]} counterclockwise about its center by an angle of {invert_pi_expression(inputs[1])} radians. Label the vertices of the resulting polygon {outputs[:-1]}, in correspondence to the vertices of {inputs[0]}.",
                f"Draw the polygon {outputs[-1]} by rotating {inputs[0]} counterclockwise about its center by an angle of {invert_pi_expression(inputs[1])} radians. Label the vertices of the resulting polygon {outputs[:-1]}, in correspondence to the vertices of {inputs[0]}."
            ]
            translated_line = random.choice(polygon_templates)
            result_lines.append(translated_line)
            continue
        
        if cmd == "measure":
            try:
                if "polygon" in command_constructed_by[raw_inputs[0]].name:
                    measure_templates = [
                        f"What is the area of polygon {inputs[0]}?",
                        f"Find the area of polygon {inputs[0]}."
                    ]
                    translated_line = random.choice(measure_templates)
                    result_lines.append(translated_line)
                    stats["measure_type"] = "area"
                    continue
            except Exception as e:
                pdb.set_trace()
            if "angle_ppp" in command_constructed_by[raw_inputs[0]].name:
                measure_templates = [
                    f"What is the measure of angle {inputs[0]}, in radians?",
                    f"Find the measure of angle {inputs[0]}, in radians."
                ]
                translated_line = random.choice(measure_templates)
                result_lines.append(translated_line)
                stats["measure_type"] = "angle"
                continue
            if "segment" in command_constructed_by[raw_inputs[0]].name:
                measure_templates = [
                    f"What is the length of segment {inputs[0]}?",
                    f"Find the length of segment {inputs[0]}."
                ]
                translated_line = random.choice(measure_templates)
                result_lines.append(translated_line)
                stats["measure_type"] = "segment_length"
                continue
            # in the following cases, we are actually measuring a Measure that was constructed by the previous command
            if "distance_pp" in command_constructed_by[raw_inputs[0]].name:
                result_lines.pop()
                last_line_inputs = command_constructed_by[raw_inputs[0]].inputs
                measure_templates = [
                    f"What is the distance between points {last_line_inputs[0]} and {last_line_inputs[1]}?",
                    f"Find the distance between points {last_line_inputs[0]} and {last_line_inputs[1]}."
                ]
                translated_line = random.choice(measure_templates)
                result_lines.append(translated_line)
                stats["measure_type"] = "two_points_distance"
                continue
            if "radius_c" in command_constructed_by[raw_inputs[0]].name:
                result_lines.pop()
                last_line_inputs = command_constructed_by[raw_inputs[0]].inputs
                measure_templates = [
                    f"What is the radius of circle {last_line_inputs[0]}?",
                    f"Find the radius of circle {last_line_inputs[0]}."
                ]
                translated_line = random.choice(measure_templates)
                result_lines.append(translated_line)
                stats["measure_type"] = "circle_radius"
                continue
            if "area_P" in command_constructed_by[raw_inputs[0]].name:
                result_lines.pop()
                last_line_inputs = command_constructed_by[raw_inputs[0]].inputs
                measure_templates = [
                    f"What is the area of polygon {last_line_inputs[0]}?",
                    f"Find the area of polygon {last_line_inputs[0]}."
                ]
                translated_line = random.choice(measure_templates)
                result_lines.append(translated_line)
                stats["measure_type"] = "area"
                continue

            measure_templates = [
                f"Compute the value of {inputs[0]}.",
                f"Calculate the value of {inputs[0]}."
            ]
            translated_line = random.choice(measure_templates)
            result_lines.append(translated_line)
            stats["measure_type"] = "other"
            continue
            
        # Get the template for this command
        template_options = command_templates.get(cmd)
        if not template_options:
            # Skip unknown commands
            # continue
            print(f"Unknown command: {cmd}")
            raise # for now

        # Randomly select one of the template options
        template = random.choice(template_options)

        # Format the template differently based on the number of outputs
        try:
            # Commands with variable outputs (like intersections)
            if len(outputs) > 1 and cmd.startswith(("intersect_", "tangent_")):
                # Handle multiple output points
                if len(outputs) == 2:
                    output_str = f"{outputs[0]} and {outputs[1]}"
                else:
                    output_str = ", ".join(outputs[:-1]) + ", and " + outputs[-1]
                
                # Modify template format for multiple outputs
                if "point" in template:
                    template = template.replace("point {0}", "points " + output_str)
                elif "line" in template:
                    template = template.replace("line {0}", "lines " + output_str)
                elif "bisector" in template:
                    template = template.replace("bisector(s) {0}", "bisectors " + output_str)
                template = template.replace("{1}", "{0}").replace("{2}", "{1}")
                # Apply the template with inputs only
                translated_line = template.format(*inputs)
            else:
                # Standard case - single output or non-intersection commands
                format_args = outputs + inputs
                translated_line = template.format(*format_args)
                
            result_lines.append(translated_line)
        except Exception as e:
            # For debugging
            print(f"Error formatting line: {line}")
            print(f"Command: {cmd}")
            print(f"Template: {template}")
            print(f"Format args: {outputs + inputs}")
            print(f"Exception: {e}")
            # continue
            raise # for now
    
    # Combine all translated lines into a coherent problem statement
    if not result_lines:
        return None, None
        
    final_result = " ".join(result_lines)
    stats["num_commands"] = num_commands
    return final_result, stats

def process_file_contents(filename: str, contents: str, answer: str, output_dir: Path, hash: str) -> None:
    problem, stats = translate_problem(contents)
    if problem is None:
        return
    with file_lock:  # Use a lock to ensure thread-safe file writing
        with open(os.path.join(output_dir, f"{global_timestamp}_mechanically_translated.jsonl"), 'a') as f:
            f.write(json.dumps({"question": problem, "answer": answer, "hash": hash, "original_filename": filename, "stats": stats}) + "\n")


def process_timestamp_dirs(output_dir: Path, after: Optional[int] = None, hashes: Dict[str, bool] = {}, max_workers: int = 4, sequential: bool = False) -> None:
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
            if after is None or timestamp >= after:
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
    if sequential:
        for task in all_tasks:
            process_file_contents(*task)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_file_contents, *task): task[0] for task in all_tasks}
            for future in concurrent.futures.as_completed(futures):
                filename = futures[future]
                #try:
                future.result()
                # except Exception as exc:
                #     print(f"Processing of {filename} generated an exception: {exc}")

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
    parser.add_argument("--sequential", action="store_true",
                        help="Process files singlethreaded (for debugging)")
    args = parser.parse_args()
    hashes = read_hashes(args.output_dir) if args.hash_check else {}
    process_timestamp_dirs(args.output_dir, args.after, hashes, args.max_workers, args.sequential)


if __name__ == "__main__":
    main()