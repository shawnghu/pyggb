import dotenv
import os

dotenv.load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

import openai

openai.api_key = api_key

client = openai.OpenAI()

def generate_response(prompt, context=None, model="gpt-4.1-mini", num_files=10):
    try:
        messages = []
        
        # Add system message with context if provided
        if context:
            messages.append({"role": "system", "content": context})
        
        # Add user message
        messages.append({"role": "user", "content": prompt % num_files})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def create_context():
    context = "Here are the relevant files:\n\n"
    
    for filename in ["commands.py", "geo_types.py", "measure_test.py", "random_constr.py", "golden_ratio.txt", \
                      "passed/batch1/angle_bisector_length.txt", "passed/batch1/circle_radius.txt",
                      "passed/batch1/cyclic_quadrilateral.txt", "passed/batch1/incircle_radius.txt",
                      "passed/batch1/triangle_ratio.txt", "passed/batch1/triangle_altitude.txt"]:
        with open(filename, 'r') as f:
            commands_content = f.read()
        short_filename = os.path.basename(filename)
        context += f"# {short_filename}:\n```\n"
        context += commands_content
        context += "\n```\n"

    context += "\n\n As a brief explanation of the above files: \n"
    context += "All of the quoted .txt files are example 'geometric construction files'"
    context += " which specify in a narrow language a method of constructing points in the plane via 'commands', and which also meet the below described criteria.\n"
    context += "geo_types.py contains the definitions of geometric types which are part of these constructions."
    context += "commands.py contains the definitions of the various commands in the geometric constructions. Of particular interest is 'measure', which effectively outputs a floating-point number corresponding to the length of the named quantity in the given construction.\n"
    context += "Also of note are the point_pm and point_pm_pm commands, which construct points of a specific distance from existing points. These two commands are the only ways in the command language to constrain the scale of the construction, and ultimately the value of the measured quantity.\n"
    context += "Also note that commands.py defines the syntax of valid commands. A file containing syntactically invalid commands will automatically fail, so this is critical. In particular, note that the commands are of the form\n"
    context += "`<command> : <possible vars> -> <newly constructed var>`\n"
    context += "and in particular, Python code is not part of the command language. This is important to remember.\n"
    context += "Note also that the command language cannot make use of numerical literals directly. Any time a numerical value is needed, it must be assigned to a variable using the 'const int' or 'const float' commands.\n"
    context += "Note furthermore that the ONLY valid commands are the ones defined in commands.py, and that any other commands will result in the construction being rejected.\n"
    context += "For example, there is no command simply named 'segment', but there is a command 'segment_pp' which constructs a segment from two points.\n"
    context += "Explicitly, the only valid commands are: \n"
    context += "angle_ppp, angular_bisector_ll, angular_bisector_ppp, angular_bisector_ss, are_collinear_ppp, are_complementary_aa, are_concurrent, are_concurrent_lll, are_concyclic_pppp, are_congruent_aa, are_congruent_ss, are_equal_mi, are_equal_mm, are_equal_pp, are_parallel_ll, are_parallel_ls, are_parallel_rr, are_parallel_sl, are_parallel_ss, are_perpendicular_ll, are_perpendicular_lr, are_perpendicular_ls, are_perpendicular_rl, are_perpendicular_sl, are_perpendicular_ss, area, area_P, center_c, circle_pm, circle_pp, circle_ppp, circle_ps, contained_by_pc, contained_by_pl, distance_pp, equality_PP, equality_Pm, equality_aa, equality_mi, equality_mm, equality_ms, equality_pp, equality_si, equality_sm, equality_ss, intersect_Cl, intersect_cc, intersect_cl, intersect_cs, intersect_lc, intersect_ll, intersect_lr, intersect_ls, intersect_rl, intersect_rr, intersect_rs, intersect_sl, intersect_sr, intersect_ss, line_bisector_pp, line_bisector_s, line_pl, line_pp, line_pr, line_ps, measure, midpoint_pp, midpoint_s, minus_A, minus_a, minus_m, minus_mm, minus_ms, minus_sm, minus_ss, mirror_cc, mirror_cl, mirror_cp, mirror_ll, mirror_lp, mirror_pc, mirror_pl, mirror_pp, mirror_ps, orthogonal_line_pl, orthogonal_line_pr, orthogonal_line_ps, point_, point_c, point_l, point_pm, point_pmpm, point_s, polar_pc, polygon, polygon_ppi, power_mi, power_si, product_bb, product_ff, product_fm, product_iA, product_if, product_im, product_is, product_mf, product_mm, product_ms, product_sm, product_ss, prove_b, radius_c, ratio_ii, ratio_mi, ratio_mm, ratio_ms, ratio_si, ratio_sm, ratio_ss, ray_pp, rotate_pAp, rotate_pap, segment_pp, semicircle, sum_mi, sum_mm, sum_ms, sum_ss, tangent_pc, touches_cc, touches_cl, touches_lc, translate_pv, vector_pp."
    context += "One final thing to observe is that it is invalid to define the same symbol twice. For example, including the phrase "
    context += "<example>\n"
    context += "rotate_pAp : B angle_90_rad A -> C\n"
    context += "point_pm : B leg2 -> C\n"
    context += "</example>\n"
    context += "will render an entire construction invalid because the symbol 'C' is defined twice.\n"
    context += "Finally, measure_test.py provides end-to-end examples of parsing and executing the commands in the geometric constructions, as well as testing the constructions to see if they constrain the quantity of the variable named by the 'measure' command.\n"
    context += "random_constr.py, similarly, provides some examples and important functions."
    context += "Ultimately, the task is to generate a large number of files which construct some geometric object and then measure it, in such a way that the value of the measure is constrained to a specific value.\n"
    context += "measure_test.py will be used to filter out constructions which do not meet the required criteria.\n"
    context += "No particular value is placed on the elegance or educational value of the constructions generated. However, variety in constructions is desirable, subject to the above constraints.\n"

    return context


context = create_context()

prompt = """Please generate %d new geometric constructions which satisfy the criteria described in the system prompt.
Format each construction as follows:
FILE_START: construction_name_1.txt
[construction content]
FILE_END

FILE_START: construction_name_2.txt
[construction content]
FILE_END

... and so on for all such constructions.
"""
def handle_response(response):
    # Split the response into individual files
    files = response.split("FILE_START:")
    files = [file.strip() for file in files if file.strip()]
    
    # Process each file
    for file in files:
        # Extract the filename and content
        filename = file.split("\n")[0].strip()
        content = "\n".join(file.split("\n")[1:-1]).strip() # remove first line (FILE_START: filename) and last line (FILE_END)

        # Write the file to the current directory
        with open(f"generated_constructions/{filename}", 'w') as f:
            f.write(content)

for i in range(1): 
    response = generate_response(prompt, context=context, num_files=100)
    # print(response)
    handle_response(response)
    # print(response)
