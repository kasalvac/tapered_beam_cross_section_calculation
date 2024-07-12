# working bizilion lines and find bizilion inntersections

import math
from OCC.Display.SimpleGui import init_display
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Line
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape


# Preparing the vizualization
display, start_display, add_menu, add_function_to_menu = init_display()

def load_step_model(file_path):
    reader = STEPControl_Reader()
    reader.ReadFile(file_path)
    reader.TransferRoots()
    return reader.Shape()

def slice_model_with_plane(model, plane):
    section_algo = BRepAlgoAPI_Section(model, plane)
    section_algo.Build()
    return section_algo.Shape()

def draw_line_origin(direction):
    # Create an Origin
    start_pnt = gp_Pnt(0,0,0)

    # Specify the direction of the line
    line_dir = gp_Dir(direction[0], 0, direction[1])

    #Making the line
    line_origin = Geom_Line(start_pnt, line_dir).Lin()
    line_origin = BRepBuilderAPI_MakeEdge(line_origin)
    line_origin.Build()
    line_origin = line_origin.Shape()
    return line_origin

def find_intersections_in(sliced_model, line_origin): # Find the points on the inner shell
    # Finding the intersections
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform() # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution() # Get the number of intersections
    if num_intersections != 4:
        return "Error: num_intersections != 4"

    # Iterate through intersections and get the points
    points_on_plane = []
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        points_on_plane.append(intersection_point)
    intersection_points_in.append(points_on_plane[0])# But only save the first two points since they are the innner points
    intersection_points_in.append( points_on_plane[1])
    return intersection_points_in

def find_intersections_out(sliced_model, line_origin): # Find the points on the outer shell
    # Finding the intersections
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform() # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution() # Get the number of intersections
    if num_intersections != 4:
        return "Error: num_intersections != 4"

    # Iterate through intersections and get the points
    points_on_plane = []
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        points_on_plane.append(intersection_point)
    intersection_points_out.append(points_on_plane[2]) # But only save the last two points since they are the outer points
    intersection_points_out.append(points_on_plane[3])
    return intersection_points_out



# Definition the plane
x_plane = 10
point_on_plane = gp_Pnt(0, 0, 0)  # Point on the plane
normal_to_plane = gp_Dir(0, 1, 0)  # Normal vector to the plane
plane = gp_Pln(point_on_plane, normal_to_plane)

# Load the STEP model
step_model_path = "Fluegelhuelle_Test3.stp"
step_model = load_step_model(step_model_path)

# Slicing of the model - extracting the wire model
sliced_model = slice_model_with_plane(step_model, plane)# Slice the model with the plane


intersection_points_in = [] # Declare empty list for inner shell
intersection_points_out = [] # Declare empty list for outer shell
desired_num_points = 100
for i in range(1, desired_num_points + 1):
    angle_pich = math.pi / desired_num_points
    cur_angle = i * angle_pich
    direction =  (math.sin(cur_angle), math.cos(cur_angle))
    line_origin = draw_line_origin(direction)
    intersection_points_in = find_intersections_in(sliced_model, line_origin)
    intersection_points_out = find_intersections_out(sliced_model, line_origin)

# print('inner shell')
# print(intersection_points_in)
# print('outer shell')
# print(intersection_points_out)
    
for point in intersection_points_in:
    display.DisplayShape(point, color="blue")

for point in intersection_points_out:
    display.DisplayShape(point, color="green")

# Making the points and lines that will intersect the shape
# direction = (1, 0)  # Direction vector
# line_origin = draw_line_origin(direction)

# intersection_points = find_intersections(sliced_model, line_origin)

# x = intersection_points[0].X()
# print(f"X coordinate: {x}")


# Vizualization
# display.DisplayShape(line_origin)
# display.DisplayShape(step_model, color="blue")
display.DisplayShape(sliced_model, color="red")
# display.View_Iso()
display.FitAll()
start_display()
