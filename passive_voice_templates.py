import random
from typing import Dict
from random_constr import Element
from translate_utils import format_vertex_list, invert_pi_expression

# These are written in the passive voice, i.e, they describe the action that has been performed.
# This is how AIME problems are worded.
def format_regular_command(command, idents: Dict[Element, str]):
    output_labels = [e.label for e in command.output_elements]
    input_labels = [idents[e] if e in idents else e.label for e in command.input_elements]
    if command.name == "point_c":
        return random.choice([
            f"A point {output_labels[0]} is constructed on circle {input_labels[0]}.",
            f"A point {output_labels[0]} is placed anywhere on circle {input_labels[0]}.",
            f"A point {output_labels[0]} is created that lies on circle {input_labels[0]}.",
            f"A point {output_labels[0]} is positioned somewhere on circle {input_labels[0]}."
        ])
    if command.name == "point_l":
        return random.choice([
            f"A point {output_labels[0]} is constructed on line {input_labels[0]}.",
            f"A point {output_labels[0]} is placed anywhere on line {input_labels[0]}.",
            f"A point {output_labels[0]} is created situated on line {input_labels[0]}.",
            f"A point {output_labels[0]} is positioned at any location on line {input_labels[0]}."
        ])
    if command.name == "point_s":
        return random.choice([
            f"A point {output_labels[0]} is constructed on segment {input_labels[0]}.",
            f"A point {output_labels[0]} is placed anywhere on segment {input_labels[0]}.",
            f"A point {output_labels[0]} is created situated on segment {input_labels[0]}.",
            f"A point {output_labels[0]} is positioned at any location on segment {input_labels[0]}."
        ])
    if command.name == "point_pm":
        return random.choice([
            f"A point {output_labels[0]} is constructed at distance {input_labels[1]} from point {input_labels[0]}.",
            f"A point {output_labels[0]} is placed that is {input_labels[1]} units away from point {input_labels[0]}.",
            f"A point {output_labels[0]} is created at a distance of {input_labels[1]} from point {input_labels[0]}.",
            f"A point {output_labels[0]} is positioned so that it is exactly {input_labels[1]} units from point {input_labels[0]}."
        ])
    if command.name == "point_at_distance":
        return random.choice([
            f"A point {output_labels[0]} is constructed at distance {input_labels[1]} from point {input_labels[0]} in a random direction.",
            f"A point {output_labels[0]} is placed so that it is {input_labels[1]} units away from point {input_labels[0]} in any direction.",
            f"A point {output_labels[0]} is created such that it lies {input_labels[1]} units from point {input_labels[0]} in any direction.",
            f"A point {output_labels[0]} is positioned at a distance of {input_labels[1]} from point {input_labels[0]}, in an arbitrary direction."
        ])
    if command.name == "point_at_distance_along_line":
        return random.choice([
            f"A point {output_labels[0]} is constructed on line {input_labels[0]}, at distance {input_labels[2]} from point {input_labels[1]}.",
            f"A point {output_labels[0]} is placed on line {input_labels[0]} such that it is {input_labels[2]} units away from point {input_labels[1]}.",
            f"A point {output_labels[0]} is created on line {input_labels[0]} so that its distance from point {input_labels[1]} is {input_labels[2]}.",
            f"A point {output_labels[0]} is positioned on line {input_labels[0]}, exactly {input_labels[2]} units away from point {input_labels[1]}."
        ])
    
    # Line creation
    if command.name == "line_pp":
        return random.choice([
            f"A line {output_labels[0]} is constructed through points {input_labels[0]} and {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn that passes through points {input_labels[0]} and {input_labels[1]}.",
            f"A line {output_labels[0]} is created connecting points {input_labels[0]} and {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through points {input_labels[0]} and {input_labels[1]}.",
            f"A line {output_labels[0]} is established passing through both points {input_labels[0]} and {input_labels[1]}."
        ])
    if command.name == "line_pl":
        return random.choice([
            f"A line {output_labels[0]} is constructed through point {input_labels[0]} parallel to line {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn passing through point {input_labels[0]} that is parallel to line {input_labels[1]}.",
            f"A line {output_labels[0]} is created through point {input_labels[0]} that never intersects line {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through point {input_labels[0]} parallel to line {input_labels[1]}.",
        "A line {0} is established through point {1} that runs parallel to line {2}."
        ])
    if command.name == "line_pr":
        return random.choice([
            f"A line {output_labels[0]} is constructed through point {input_labels[0]} parallel to ray {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn passing through point {input_labels[0]} that is parallel to ray {input_labels[1]}.",
            f"A line {output_labels[0]} is created through point {input_labels[0]} that never intersects ray {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through point {input_labels[0]} parallel to ray {input_labels[1]}.",
            f"A line {output_labels[0]} is established through point {input_labels[0]} that runs parallel to ray {input_labels[1]}."
        ])
    if command.name == "line_ps":
        return random.choice([
            f"A line {output_labels[0]} is constructed through point {input_labels[0]} parallel to segment {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn passing through point {input_labels[0]} that is parallel to segment {input_labels[1]}.",
            f"A line {output_labels[0]} is created through point {input_labels[0]} that runs in the same direction as segment {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through point {input_labels[0]} parallel to segment {input_labels[1]}.",
            f"A line {output_labels[0]} is established through point {input_labels[0]} that is parallel to segment {input_labels[1]}."
        ])
    if command.name == "line_bisector_pp":
        return random.choice([
            f"The perpendicular bisector {output_labels[0]} of points {input_labels[0]} and {input_labels[1]} is constructed.",
            f"The perpendicular bisector {output_labels[0]} of the line segment connecting points {input_labels[0]} and {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the perpendicular bisector of the segment between points {input_labels[0]} and {input_labels[1]}.",
            f"The line {output_labels[0]} is formed as the perpendicular bisector of the segment from point {input_labels[0]} to point {input_labels[1]}.",
            f"The line {output_labels[0]} is established that divides the segment between {input_labels[0]} and {input_labels[1]} into two equal parts and is perpendicular to it."
        ])
    if command.name == "line_bisector_s":
        return random.choice([
            f"The perpendicular bisector {output_labels[0]} of segment {input_labels[0]} is constructed.",
            f"The perpendicular bisector {output_labels[0]} that divides segment {input_labels[0]} into two equal parts is drawn.",
            f"Let {output_labels[0]} be the perpendicular bisector of segment {input_labels[0]}.",
            f"The perpendicular bisector {output_labels[0]} is formed that cuts segment {input_labels[0]} into two equal halves.",
            f"The line {output_labels[0]} is established that is perpendicular to segment {input_labels[0]} and passes through its midpoint."
        ])
    
    # Orthogonal lines
    if command.name == "orthogonal_line_pl":
        return random.choice([
            f"A line {output_labels[0]} is constructed through point {input_labels[0]} perpendicular to line {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn passing through point {input_labels[0]} that is perpendicular to line {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through point {input_labels[0]} perpendicular to line {input_labels[1]}.",
            f"A line {output_labels[0]} is formed through point {input_labels[0]} that is at a 90-degree angle to line {input_labels[1]}.",
            f"A line {output_labels[0]} is established through point {input_labels[0]} that is orthogonal to line {input_labels[1]}."
        ])
    if command.name == "orthogonal_line_pr":
        return random.choice([
            f"A line {output_labels[0]} is constructed through point {input_labels[0]} perpendicular to ray {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn passing through point {input_labels[0]} that is perpendicular to ray {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through point {input_labels[0]} perpendicular to ray {input_labels[1]}.",
            f"A line {output_labels[0]} is formed through point {input_labels[0]} that is at a 90-degree angle to ray {input_labels[1]}.",
            f"A line {output_labels[0]} is established through point {input_labels[0]} that is orthogonal to ray {input_labels[1]}."
        ])
    if command.name == "orthogonal_line_ps":
        return random.choice([
            f"A line {output_labels[0]} is constructed through point {input_labels[0]} perpendicular to segment {input_labels[1]}.",
            f"A line {output_labels[0]} is drawn passing through point {input_labels[0]} that is perpendicular to segment {input_labels[1]}.",
            f"Let {output_labels[0]} be the line through point {input_labels[0]} perpendicular to segment {input_labels[1]}.",
            f"A line {output_labels[0]} is formed through point {input_labels[0]} that is at a 90-degree angle to segment {input_labels[1]}.",
            f"A line {output_labels[0]} is established through point {input_labels[0]} that is orthogonal to segment {input_labels[1]}."
        ])
    
    # Angular bisectors
    if command.name == "angular_bisector_ll":
        return random.choice([
            f"The angle bisectors {output_labels[0]}, {output_labels[1]} of lines {input_labels[0]} and {input_labels[1]} are constructed.",
            f"The angle bisectors {output_labels[0]}, {output_labels[1]} that divide the angles formed by lines {input_labels[0]} and {input_labels[1]} are drawn.",
            f"Let {output_labels[0]} and {output_labels[1]} be the angle bisectors of the angles between lines {input_labels[0]} and {input_labels[1]}.",
            f"The angle bisectors {output_labels[0]}, {output_labels[1]} are formed for the angles created by lines {input_labels[0]} and {input_labels[1]}.",
            f"The lines {output_labels[0]}, {output_labels[1]} are established that divide the angles between lines {input_labels[0]} and {input_labels[1]} into equal parts."
        ])
    if command.name == "angular_bisector_ppp":
        return random.choice([
            f"The angle bisector {output_labels[0]} of angle {input_labels[0]}{input_labels[1]}{input_labels[2]} is constructed.",
            f"The angle bisector {output_labels[0]} that divides angle {input_labels[0]}{input_labels[1]}{input_labels[2]} into two equal parts is drawn.",
            f"Let {output_labels[0]} be the angle bisector of angle {input_labels[0]}{input_labels[1]}{input_labels[2]}.",
            f"The angle bisector {output_labels[0]} is formed that splits angle {input_labels[0]}{input_labels[1]}{input_labels[2]} into two equal angles.",
            f"The ray {output_labels[0]} is established that divides angle {input_labels[0]}{input_labels[1]}{input_labels[2]} into two congruent angles."
        ])
    if command.name == "angular_bisector_ss":
        return random.choice([
            f"The angle bisectors {output_labels[0]}, {output_labels[1]} of segments {input_labels[0]} and {input_labels[1]} are constructed.",
            f"The angle bisectors {output_labels[0]}, {output_labels[1]} that divide the angles formed by segments {input_labels[0]} and {input_labels[1]} are drawn.",
            f"Let {output_labels[0]} and {output_labels[1]} be the angle bisectors of the angles between segments {input_labels[0]} and {input_labels[1]}.",
            f"The angle bisectors {output_labels[0]}, {output_labels[1]} are formed for the angles created by segments {input_labels[0]} and {input_labels[1]}.",
            f"The lines {output_labels[0]}, {output_labels[1]} are established that divide the angles between segments {input_labels[0]} and {input_labels[1]} into equal parts."
        ])
    
    # Intersections
    if command.name == "intersect_ll":
        return random.choice([
            f"The intersection point {output_labels[0]} of lines {input_labels[0]} and {input_labels[1]} is found.",
            f"The point {output_labels[0]} where lines {input_labels[0]} and {input_labels[1]} intersect is determined.",
            f"Let {output_labels[0]} be the point at which lines {input_labels[0]} and {input_labels[1]} cross each other.",
            f"The point {output_labels[0]} common to both lines {input_labels[0]} and {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where lines {input_labels[0]} and {input_labels[1]} meet is marked."
        ])
    if command.name == "intersect_lc":
        return random.choice([
            f"The intersection point {output_labels[0]} of line {input_labels[0]} and circle {input_labels[1]} is found.",
            f"The point {output_labels[0]} where line {input_labels[0]} intersects circle {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which line {input_labels[0]} crosses circle {input_labels[1]}.",
            f"The point {output_labels[0]} common to both line {input_labels[0]} and circle {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where line {input_labels[0]} meets circle {input_labels[1]} is marked."
        ])
    if command.name == "intersect_cs":
        return random.choice([
            f"The intersection point {output_labels[0]} of circle {input_labels[0]} and segment {input_labels[1]} is found.",
            f"The point {output_labels[0]} where circle {input_labels[0]} intersects segment {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which circle {input_labels[0]} crosses segment {input_labels[1]}.",
            f"The point {output_labels[0]} common to both circle {input_labels[0]} and segment {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where circle {input_labels[0]} meets segment {input_labels[1]} is marked."
        ])
    if command.name == "intersect_cc":
        return random.choice([
            f"The intersection point {output_labels[0]} of circles {input_labels[0]} and {input_labels[1]} is found.",
            f"The point {output_labels[0]} where circles {input_labels[0]} and {input_labels[1]} intersect is determined.",
            f"Let {output_labels[0]} be the point at which circles {input_labels[0]} and {input_labels[1]} cross each other.",
            f"The point {output_labels[0]} common to both circles {input_labels[0]} and {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where circles {input_labels[0]} and {input_labels[1]} meet is marked."
        ])
    if command.name == "intersect_cl":
        return random.choice([
            f"The intersection point {output_labels[0]} of circle {input_labels[0]} and line {input_labels[1]} is found.",
            f"The point {output_labels[0]} where circle {input_labels[0]} intersects line {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which circle {input_labels[0]} crosses line {input_labels[1]}.",
            f"The point {output_labels[0]} common to both circle {input_labels[0]} and line {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where circle {input_labels[0]} meets line {input_labels[1]} is marked."
        ])
    if command.name == "intersect_lr":
        return random.choice([
            f"The intersection point {output_labels[0]} of line {input_labels[0]} and ray {input_labels[1]} is found.",
            f"The point {output_labels[0]} where line {input_labels[0]} intersects ray {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which line {input_labels[0]} crosses ray {input_labels[1]}.",
            f"The point {output_labels[0]} common to both line {input_labels[0]} and ray {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where line {input_labels[0]} meets ray {input_labels[1]} is marked."
        ])
    if command.name == "intersect_ls":
        return random.choice([
            f"The intersection point {output_labels[0]} of line {input_labels[0]} and segment {input_labels[1]} is found.",
            f"The point {output_labels[0]} where line {input_labels[0]} intersects segment {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which line {input_labels[0]} crosses segment {input_labels[1]}.",
            f"The point {output_labels[0]} common to both line {input_labels[0]} and segment {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where line {input_labels[0]} meets segment {input_labels[1]} is marked."
        ])
    if command.name == "intersect_rl":
        return random.choice([
            f"The intersection point {output_labels[0]} of ray {input_labels[0]} and line {input_labels[1]} is found.",
            f"The point {output_labels[0]} where ray {input_labels[0]} intersects line {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which ray {input_labels[0]} crosses line {input_labels[1]}.",
            f"The point {output_labels[0]} common to both ray {input_labels[0]} and line {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where ray {input_labels[0]} meets line {input_labels[1]} is marked."
        ])
    if command.name == "intersect_rr":
        return random.choice([
            f"The intersection point {output_labels[0]} of rays {input_labels[0]} and {input_labels[1]} is found.",
            f"The point {output_labels[0]} where rays {input_labels[0]} and {input_labels[1]} intersect is determined.",
            f"Let {output_labels[0]} be the point at which rays {input_labels[0]} and {input_labels[1]} cross each other.",
            f"The point {output_labels[0]} common to both rays {input_labels[0]} and {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where rays {input_labels[0]} and {input_labels[1]} meet is marked."
        ])
    if command.name == "intersect_rs":
        return random.choice([
            f"The intersection point {output_labels[0]} of ray {input_labels[0]} and segment {input_labels[1]} is found.",
            f"The point {output_labels[0]} where ray {input_labels[0]} intersects segment {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which ray {input_labels[0]} crosses segment {input_labels[1]}.",
            f"The point {output_labels[0]} common to both ray {input_labels[0]} and segment {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where ray {input_labels[0]} meets segment {input_labels[1]} is marked."
        ])
    if command.name == "intersect_sl":
        return random.choice([
            f"The intersection point {output_labels[0]} of segment {input_labels[0]} and line {input_labels[1]} is found.",
            f"The point {output_labels[0]} where segment {input_labels[0]} intersects line {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which segment {input_labels[0]} crosses line {input_labels[1]}.",
            f"The point {output_labels[0]} common to both segment {input_labels[0]} and line {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where segment {input_labels[0]} meets line {input_labels[1]} is marked."
        ])
    if command.name == "intersect_sr":
        return random.choice([
            f"The intersection point {output_labels[0]} of segment {input_labels[0]} and ray {input_labels[1]} is found.",
            f"The point {output_labels[0]} where segment {input_labels[0]} intersects ray {input_labels[1]} is determined.",
            f"Let {output_labels[0]} be the point at which segment {input_labels[0]} crosses ray {input_labels[1]}.",
            f"The point {output_labels[0]} common to both segment {input_labels[0]} and ray {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where segment {input_labels[0]} meets ray {input_labels[1]} is marked."
        ])
    if command.name == "intersect_ss":
        return random.choice([
            f"The intersection point {output_labels[0]} of segments {input_labels[0]} and {input_labels[1]} is found.",
            f"The point {output_labels[0]} where segments {input_labels[0]} and {input_labels[1]} intersect is determined.",
            f"Let {output_labels[0]} be the point at which segments {input_labels[0]} and {input_labels[1]} cross each other.",
            f"The point {output_labels[0]} common to both segments {input_labels[0]} and {input_labels[1]} is identified.",
            f"The point {output_labels[0]} where segments {input_labels[0]} and {input_labels[1]} meet is marked."
        ])
    
    # Circles
    if command.name == "circle_pp":
        return random.choice([
            f"A circle {output_labels[0]} with center {input_labels[0]} passing through point {input_labels[1]} is constructed.",
            f"A circle {output_labels[0]} centered at {input_labels[0]} that passes through point {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the circle with center at {input_labels[0]} and containing point {input_labels[1]} on its circumference.",
            f"A circle {output_labels[0]} is formed centered at point {input_labels[0]} such that point {input_labels[1]} lies on it.",
            f"A circle {output_labels[0]} is established with center {input_labels[0]} and radius equal to the distance from {input_labels[0]} to {input_labels[1]}."
        ])
    if command.name == "circle_ppp":
        return random.choice([
            f"A circle {output_labels[0]} passing through points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} is constructed.",
            f"A circle {output_labels[0]} that passes through the three points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} is drawn.",
            f"Let {output_labels[0]} be the circle containing points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} on its circumference.",
            f"A circle {output_labels[0]} is formed such that points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} all lie on it.",
            f"A circle {output_labels[0]} is established that passes through each of the points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]}."
        ])
    if command.name == "circle_pm":
        return random.choice([
            f"A circle {output_labels[0]} with center {input_labels[0]} and radius {input_labels[1]} is constructed.",
            f"A circle {output_labels[0]} centered at {input_labels[0]} with a radius of {input_labels[1]} units is drawn.",
            f"Let {output_labels[0]} be the circle with center at point {input_labels[0]} and radius equal to {input_labels[1]}.",
            f"A circle {output_labels[0]} is formed centered at {input_labels[0]} with a distance of {input_labels[1]} from center to circumference.",
            f"A circle {output_labels[0]} is established with center point {input_labels[0]} and radius measuring {input_labels[1]} units."
        ])
    if command.name == "circle_ps":
        return random.choice([
            f"A circle {output_labels[0]} with center {input_labels[0]} and radius equal to the length of segment {input_labels[1]} is constructed.",
            f"A circle {output_labels[0]} centered at {input_labels[0]} with radius equal to the length of segment {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the circle with center at point {input_labels[0]} and radius matching the length of segment {input_labels[1]}.",
            f"A circle {output_labels[0]} is formed centered at {input_labels[0]} with a radius that equals the length of segment {input_labels[1]}.",
            f"A circle {output_labels[0]} is established with center point {input_labels[0]} and radius identical to the length of segment {input_labels[1]}."
        ])
    if command.name == "center_c":
        return random.choice([
            f"Let {output_labels[0]} be the center of circle {input_labels[0]}.",
            f"The point {output_labels[0]} is marked as the center of circle {input_labels[0]}.",
            f"The point {output_labels[0]} is identified as the center point of circle {input_labels[0]}.",
            f"The point {output_labels[0]} is designated as the center of circle {input_labels[0]}.",
            f"The point {output_labels[0]} is defined to be the center of circle {input_labels[0]}."
        ])
    
    # Segments
    if command.name == "segment_pp":
        return random.choice([
            f"A segment {output_labels[0]} from point {input_labels[0]} to point {input_labels[1]} is constructed.",
            f"A line segment {output_labels[0]} connecting points {input_labels[0]} and {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the line segment between points {input_labels[0]} and {input_labels[1]}.",
            f"A segment {output_labels[0]} is formed joining points {input_labels[0]} and {input_labels[1]}.",
            f"A line segment {output_labels[0]} is established from point {input_labels[0]} to point {input_labels[1]}."
        ])
    
    # Midpoints
    if command.name == "midpoint_pp":
        return random.choice([
            f"The midpoint {output_labels[0]} of points {input_labels[0]} and {input_labels[1]} is found.",
            f"The midpoint {output_labels[0]} between points {input_labels[0]} and {input_labels[1]} is located.",
            f"Let {output_labels[0]} be the point that is equidistant from points {input_labels[0]} and {input_labels[1]}.",
            f"The midpoint {output_labels[0]} of the segment connecting points {input_labels[0]} and {input_labels[1]} is identified.",
            f"The point {output_labels[0]} that divides the segment from {input_labels[0]} to {input_labels[1]} into two equal parts is marked."
        ])
    
    # Midpoints
    if command.name == "midpoint_s":
        return random.choice([
            f"The midpoint {output_labels[0]} of segment {input_labels[0]} is found.",
            f"The midpoint {output_labels[0]} of segment {input_labels[0]} is located.",
            f"Let {output_labels[0]} be the point that divides segment {input_labels[0]} into two equal parts.",
            f"The point {output_labels[0]} at the middle of segment {input_labels[0]} is identified.",
            f"The point {output_labels[0]} that is equidistant from both endpoints of segment {input_labels[0]} is marked."
        ])
    
    # Reflections/Mirrors
    if command.name == "mirror_pp":
        return random.choice([
            f"Point {output_labels[0]} is constructed as the reflection of point {input_labels[0]} across point {input_labels[1]}.",
            f"Point {output_labels[0]} is created as the reflection of point {input_labels[0]} across point {input_labels[1]}.",
            f"Let {output_labels[0]} be the point such that point {input_labels[1]} is the midpoint of the segment from {input_labels[0]} to {output_labels[0]}.",
            f"Point {output_labels[0]} is determined by reflecting point {input_labels[0]} through point {input_labels[1]}.",
            f"Point {output_labels[0]} is constructed as the image of point {input_labels[0]} when reflected over point {input_labels[1]}."
        ])
    if command.name == "mirror_pl":
        return random.choice([
            f"Point {output_labels[0]} is constructed as the reflection of point {input_labels[0]} across line {input_labels[1]}.",
            f"Point {output_labels[0]} is created as the reflection of point {input_labels[0]} across line {input_labels[1]}.",
            f"Let {output_labels[0]} be the point such that line {input_labels[1]} is the perpendicular bisector of segment from {input_labels[0]} to {output_labels[0]}.",
            f"Point {output_labels[0]} is determined by reflecting point {input_labels[0]} over line {input_labels[1]}.",
            f"Point {output_labels[0]} is constructed as the image of point {input_labels[0]} when reflected across line {input_labels[1]}."
        ])
    if command.name == "mirror_ps":
        return random.choice([
            f"Point {output_labels[0]} is constructed as the reflection of point {input_labels[0]} across segment {input_labels[1]}.",
            f"Point {output_labels[0]} is created as the reflection of point {input_labels[0]} across segment {input_labels[1]}.",
            f"Let {output_labels[0]} be the point obtained by reflecting point {input_labels[0]} over segment {input_labels[1]}.",
            f"Point {output_labels[0]} is determined as the mirror image of point {input_labels[0]} with segment {input_labels[1]} as the mirror.",
            f"Point {output_labels[0]} is constructed as the image of point {input_labels[0]} when reflected across segment {input_labels[1]}."
        ])
    if command.name == "mirror_pc":
        return random.choice([
            f"Point {output_labels[0]} is constructed as the inversion of point {input_labels[0]} with respect to circle {input_labels[1]}.",
            f"Point {output_labels[0]} is created as the inversion of point {input_labels[0]} with respect to circle {input_labels[1]}.",
            f"Let {output_labels[0]} be the point obtained by inverting point {input_labels[0]} in circle {input_labels[1]}.",
            f"Point {output_labels[0]} is determined as the result of inverting point {input_labels[0]} with respect to circle {input_labels[1]}.",
            f"Point {output_labels[0]} is constructed as the image of point {input_labels[0]} under inversion in circle {input_labels[1]}."
        ])
    if command.name == "mirror_lp":
        return random.choice([
            f"Line {output_labels[0]} is constructed as the reflection of line {input_labels[0]} across point {input_labels[1]}.",
            f"Line {output_labels[0]} is created as the reflection of line {input_labels[0]} across point {input_labels[1]}.",
            f"Let {output_labels[0]} be the line obtained by reflecting line {input_labels[0]} through point {input_labels[1]}.",
            f"Line {output_labels[0]} is determined as the mirror image of line {input_labels[0]} with point {input_labels[1]} as the center of reflection.",
            f"Line {output_labels[0]} is constructed as the image of line {input_labels[0]} when reflected over point {input_labels[1]}."
        ])
    if command.name == "mirror_ll":
        return random.choice([
            f"Line {output_labels[0]} is constructed as the reflection of line {input_labels[0]} across line {input_labels[1]}.",
            f"Line {output_labels[0]} is created as the reflection of line {input_labels[0]} across line {input_labels[1]}.",
            f"Let {output_labels[0]} be the line obtained by reflecting line {input_labels[0]} over line {input_labels[1]}.",
            f"Line {output_labels[0]} is determined as the mirror image of line {input_labels[0]} with line {input_labels[1]} as the mirror.",
            f"Line {output_labels[0]} is constructed as the image of line {input_labels[0]} when reflected across line {input_labels[1]}."
        ])
    if command.name == "mirror_cl":
        return random.choice([
            f"Circle {output_labels[0]} is constructed as the reflection of circle {input_labels[0]} across line {input_labels[1]}.",
            f"Circle {output_labels[0]} is created as the reflection of circle {input_labels[0]} across line {input_labels[1]}.",
            f"Let {output_labels[0]} be the circle obtained by reflecting circle {input_labels[0]} over line {input_labels[1]}.",
            f"Circle {output_labels[0]} is determined as the mirror image of circle {input_labels[0]} with line {input_labels[1]} as the mirror.",
            f"Circle {output_labels[0]} is constructed as the image of circle {input_labels[0]} when reflected across line {input_labels[1]}."
        ])
    if command.name == "mirror_cp":
        return random.choice([
            f"Circle {output_labels[0]} is constructed as the reflection of circle {input_labels[0]} across point {input_labels[1]}.",
            f"Circle {output_labels[0]} is created as the reflection of circle {input_labels[0]} across point {input_labels[1]}.",
            f"Let {output_labels[0]} be the circle obtained by reflecting circle {input_labels[0]} through point {input_labels[1]}.",
            f"Circle {output_labels[0]} is determined as the mirror image of circle {input_labels[0]} with point {input_labels[1]} as the center of reflection.",
            f"Circle {output_labels[0]} is constructed as the image of circle {input_labels[0]} when reflected over point {input_labels[1]}."
        ])
    
    # Angles
    if command.name == "angle_ppp":
        return random.choice([
            f"The angle {output_labels[0]} formed by points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} is measured.",
            f"The angle {output_labels[0]} with vertex at point {input_labels[1]}, formed by rays from {input_labels[1]} to {input_labels[0]} and from {input_labels[1]} to {input_labels[2]}, is determined.",
            f"Let {output_labels[0]} be the measure of the angle formed by points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]}, with {input_labels[1]} as the vertex.",
            f"The angle {output_labels[0]} is calculated as the measure of angle {input_labels[0]}{input_labels[1]}{input_labels[2]}.",
            f"The measure of angle {input_labels[0]}{input_labels[1]}{input_labels[2]} is found and labeled as {output_labels[0]}."
        ])
    
    # these actually should not matter; since these compute a Measure the only thing that can follow them is a "measure" command, and that will handle the actual translation of these commands
    if command.name == "distance_pp":
        return random.choice([
            f"The distance between points {input_labels[0]} and {input_labels[1]} is measured.",
            f"The distance between points {input_labels[0]} and {input_labels[1]} is found.",
            f"Let {output_labels[0]} be the distance between points {input_labels[0]} and {input_labels[1]}.",
        ])
    if command.name == "radius_c":
        return random.choice([
            f"The radius of circle {input_labels[0]} is measured.",
            f"The radius of circle {input_labels[0]} is found.",
            f"Let {output_labels[0]} be the radius of circle {input_labels[0]}.",
        ])
    if command.name == "area_P":
        return random.choice([
            f"The area of polygon {input_labels[0]} is calculated.",
            f"The area of polygon {input_labels[0]} is found.",
            f"Let {output_labels[0]} be the area of polygon {input_labels[0]}.",
        ])
    
    # Ray
    if command.name == "ray_pp":
        return random.choice([
            f"A ray {output_labels[0]} starting at point {input_labels[0]} and passing through point {input_labels[1]} is constructed.",
            f"A ray {output_labels[0]} with endpoint at {input_labels[0]} that passes through point {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the ray originating from point {input_labels[0]} and extending through point {input_labels[1]}.",
            f"A ray {output_labels[0]} is formed with its vertex at {input_labels[0]} and passing through point {input_labels[1]}.",
        ])
    
    # Rotations
    if command.name == "rotate_pap":
        return random.choice([
            f"Point {output_labels[0]} is constructed by rotating point {input_labels[0]} by an angle of {invert_pi_expression(input_labels[1])} radians about point {input_labels[2]}.",
            f"Point {output_labels[0]} is created by turning point {input_labels[0]} by {invert_pi_expression(input_labels[1])} radians around the fixed point {input_labels[2]}.",
            f"Let {output_labels[0]} be the point obtained by rotating point {input_labels[0]} counterclockwise by {invert_pi_expression(input_labels[1])} radians around point {input_labels[2]}.",
            f"Point {output_labels[0]} is determined as the image of point {input_labels[0]} when rotated by an angle of {invert_pi_expression(input_labels[1])} radians about point {input_labels[2]}.",
            f"Point {output_labels[0]} is constructed by turning point {input_labels[0]} through an angle of {invert_pi_expression(input_labels[1])} radians around the fixed point {input_labels[2]}."
        ])
    if command.name == "rotate_pAp":
        return random.choice([
            f"Point {output_labels[0]} is constructed by rotating point {input_labels[0]} by an angle equal to the measure of angle {input_labels[1]} about point {input_labels[2]}.",
            f"Point {output_labels[0]} is created by turning point {input_labels[0]} by the same angle as {input_labels[1]} around the fixed point {input_labels[2]}.",
            f"Let {output_labels[0]} be the point obtained by rotating point {input_labels[0]} counterclockwise by an angle equal to {input_labels[1]} around point {input_labels[2]}.",
            f"Point {output_labels[0]} is determined as the image of point {input_labels[0]} when rotated by an angle equivalent to {input_labels[1]} about point {input_labels[2]}.",
            f"Point {output_labels[0]} is constructed by turning point {input_labels[0]} through an angle matching the measure of {input_labels[1]} around the fixed point {input_labels[2]}."
        ])
    
    # Vectors
    if command.name == "vector_pp":
        return random.choice([
            f"A vector {output_labels[0]} from point {input_labels[0]} to point {input_labels[1]} is constructed.",
            f"A vector {output_labels[0]} directed from point {input_labels[0]} to point {input_labels[1]} is created.",
            f"Let {output_labels[0]} be the vector starting at point {input_labels[0]} and ending at point {input_labels[1]}.",
            f"A vector {output_labels[0]} is formed with initial point {input_labels[0]} and terminal point {input_labels[1]}.",
            f"A vector {output_labels[0]} is established pointing from point {input_labels[0]} toward point {input_labels[1]}."
        ])
    if command.name == "translate_pv":
        return random.choice([
            f"Point {output_labels[0]} is translated by vector {input_labels[1]}, and the resulting point is called {input_labels[0]}.",
            f"Point {output_labels[0]} is created by translating point {input_labels[0]} along vector {input_labels[1]}.",
            f"Let {output_labels[0]} be the point obtained by moving point {input_labels[0]} according to vector {input_labels[1]}.",
            f"Point {output_labels[0]} is determined as the image of point {input_labels[0]} when translated by vector {input_labels[1]}.",
            f"Point {output_labels[0]} is constructed by shifting point {input_labels[0]} in the direction and magnitude of vector {input_labels[1]}."
        ])
    
    # Tangents
    if command.name == "tangent_pc":
        return random.choice([
            f"The tangent line {output_labels[0]} from point {input_labels[0]} to circle {input_labels[1]} is constructed.",
            f"The tangent line {output_labels[0]} that passes through point {input_labels[0]} and touches circle {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the line passing through point {input_labels[0]} that is tangent to circle {input_labels[1]}.",
            f"The tangent line {output_labels[0]} from point {input_labels[0]} to circle {input_labels[1]} is formed.",
            f"The line {output_labels[0]} through point {input_labels[0]} that touches circle {input_labels[1]} at exactly one point is established."
        ])
    if command.name == "polar_pc":
        return random.choice([
            f"The polar line {output_labels[0]} of point {input_labels[0]} with respect to circle {input_labels[1]} is constructed.",
            f"The polar line {output_labels[0]} of point {input_labels[0]} with respect to circle {input_labels[1]} is drawn.",
            f"Let {output_labels[0]} be the polar line of point {input_labels[0]} relative to circle {input_labels[1]}.",
            f"The polar line {output_labels[0]} corresponding to point {input_labels[0]} with respect to circle {input_labels[1]} is formed.",
            f"The polar line {output_labels[0]} of point {input_labels[0]} in relation to circle {input_labels[1]} is established."
        ])
    
    # Triangle-related commands
    if command.name == "triangle_ppp":
        return random.choice([
            f"A triangle {output_labels[0]} with vertices at points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} is constructed.",
            f"A triangle {output_labels[0]} using points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]} as vertices is drawn.",
            f"Let {output_labels[0]} be the triangle whose vertices are points {input_labels[0]}, {input_labels[1]}, and {input_labels[2]}."
        ])
    if command.name == "circumcircle_t":
        return random.choice([
            f"The circumcircle {output_labels[0]} of triangle {input_labels[0]} is constructed.",
            f"The circle {output_labels[0]} that passes through all three vertices of triangle {input_labels[0]} is drawn.",
            f"Let {output_labels[0]} be the circumscribed circle of triangle {input_labels[0]}."
        ])
    if command.name == "circumcenter_t":
        return random.choice([
            f"The circumcenter {output_labels[0]} of triangle {input_labels[0]} is found.",
            f"The point {output_labels[0]} that is the center of the circumscribed circle of triangle {input_labels[0]} is located.",
            f"Let {output_labels[0]} be the circumcenter of triangle {input_labels[0]}, which is equidistant from all three vertices."
        ])
    if command.name == "circumradius_t":
        return random.choice([
            f"The circumradius {output_labels[0]} of triangle {input_labels[0]} is measured.",
            f"The length {output_labels[0]} of the radius of the circumscribed circle of triangle {input_labels[0]} is found.",
            f"Let {output_labels[0]} be the circumradius of triangle {input_labels[0]}, which is the distance from its circumcenter to any vertex."
        ])
    if command.name == "centroid_t":
        return random.choice([
            f"The centroid {output_labels[0]} of triangle {input_labels[0]} is found.",
            f"The point {output_labels[0]} that is the centroid of triangle {input_labels[0]} is located.",
            f"Let {output_labels[0]} be the centroid of triangle {input_labels[0]}, which is the point where the three medians intersect.",
            f"The centroid {output_labels[0]} of triangle {input_labels[0]} is determined as the point of concurrence of the three medians.",
            f"The point {output_labels[0]} is identified as the centroid of triangle {input_labels[0]}, located at the intersection of all medians."
        ])
    if command.name == "orthocenter_t":
        return random.choice([
            f"The orthocenter {output_labels[0]} of triangle {input_labels[0]} is found.",
            f"The point {output_labels[0]} that is the orthocenter of triangle {input_labels[0]} is located.",
            f"Let {output_labels[0]} be the orthocenter of triangle {input_labels[0]}, which is the point where the three altitudes intersect.",
            f"The orthocenter {output_labels[0]} of triangle {input_labels[0]} is determined as the point of concurrence of the three altitudes.",
            f"The point {output_labels[0]} is identified as the orthocenter of triangle {input_labels[0]}, located at the intersection of all altitudes."
        ])
    if command.name == "incircle_t":
        return random.choice([
            f"The incircle {output_labels[0]} of triangle {input_labels[0]} is constructed.",
            f"The circle {output_labels[0]} that is tangent to all three sides of triangle {input_labels[0]} is drawn.",
            f"Let {output_labels[0]} be the inscribed circle of triangle {input_labels[0]}.",
            f"The incircle {output_labels[0]} of triangle {input_labels[0]} is formed, touching each side of the triangle.",
            f"The circle {output_labels[0]} is established as the incircle of triangle {input_labels[0]}, tangent to all three sides."
        ])
    if command.name == "incenter_t":
        return random.choice([
            f"The incenter {output_labels[0]} of triangle {input_labels[0]} is found.",
            f"The point {output_labels[0]} that is the center of the inscribed circle of triangle {input_labels[0]} is located.",
            f"Let {output_labels[0]} be the incenter of triangle {input_labels[0]}, which is equidistant from all three sides.",
            f"The incenter {output_labels[0]} of triangle {input_labels[0]} is determined as the point of concurrence of the three angle bisectors.",
            f"The point {output_labels[0]} is identified as the incenter of triangle {input_labels[0]}, located at the intersection of all angle bisectors."
        ])
    if command.name == "inradius_t":
        return random.choice([
            f"The inradius {output_labels[0]} of triangle {input_labels[0]} is measured.",
            f"The length {output_labels[0]} of the radius of the inscribed circle of triangle {input_labels[0]} is found.",
            f"Let {output_labels[0]} be the inradius of triangle {input_labels[0]}, which is the distance from the incenter to any side.",
            f"The inradius {output_labels[0]} of triangle {input_labels[0]} is calculated as the radius of its inscribed circle.",
            f"The value {output_labels[0]} is determined as the inradius of triangle {input_labels[0]}, measuring from incenter to any side."
        ])
    if command.name == "circumcircle_p":
        return random.choice([
            f"Let {output_labels[0]} be the circumcircle of polygon {input_labels[0]}.",
        ])
    raise Exception(f"Unknown command: {command.name}")
    

def format_polygon_command(command, idents: Dict[Element, str]):
    output_labels = [e.label for e in command.output_elements]
    input_labels = [idents[e] if e in idents else e.label for e in command.input_elements]
    if command.name == "polygon_from_center_and_circumradius":
        num_sides = input_labels[0]
        center = input_labels[1]
        circumradius = input_labels[2]
        polygon_out = output_labels[-1]
        vertices = output_labels[:-1]
        vertices_str = ''.join(vertices)
        polygon_templates = [
                f"Let {vertices_str} be a regular {num_sides}-gon, centered at {center} with a circumradius of {circumradius}.",
                f"{vertices_str} is a regular {num_sides}-gon, centered at {center} with a circumradius of {circumradius}.",
        ]
    if command.name == "rotate_polygon_about_center_by_equivalent_angle":
        polygon_in = input_labels[0]
        angle = input_labels[1]
        polygon_out = output_labels[-1]
        vertices = output_labels[:-1]
        vertices_str = ''.join(vertices)
        polygon_templates = [
            f"{vertices_str} is drawn by rotating {polygon_in} counterclockwise about its center by an angle equal to the measure of angle {angle}.",
            f"{polygon_in} is rotated about its center counterclockwise by an angle equal to the measure of angle {angle} to form {vertices_str}."
        ]
    if command.name == "rotate_polygon_about_center":
        polygon_in = input_labels[0]
        angle = invert_pi_expression(input_labels[1])
        vertices = output_labels[:-1]
        vertices_str = ''.join(vertices)
        polygon_templates = [
            f"{vertices_str} is drawn by rotating {polygon_in} counterclockwise about its center by {angle} radians.",
            f"{polygon_in} is rotated about its center counterclockwise by {angle} radians to form {vertices_str}."
        ]
    template = random.choice(polygon_templates)
    # yes, it's extremely weird to describe a square in terms of its circumradius, but at least it is logically unambiguous.
    if num_sides == 4:
        template = template.replace("regular 4-gon", "square")
    if num_sides == 6:
        template = template.replace("6-gon", "hexagon")
    if num_sides == 8:
        template = template.replace("8-gon", "octagon")
    if num_sides == 12:
        template = template.replace("12-gon", "dodecagon")
    idents[command.output_elements[-1]] = vertices_str
    return template
        
        
