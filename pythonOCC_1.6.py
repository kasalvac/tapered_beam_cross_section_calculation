# working def find_intersections(sliced_model, line_origin):

import math
from OCC.Display.SimpleGui import init_display
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Line
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape

# from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
# from OCC.Core.TopExp import TopExp_Explorer
# from OCC.Core.TopAbs import TopAbs_EDGE
# from OCC.Core.TopoDS import topods_Edge
# from OCC.Core.BRep import BRep_Tool



# Starting the vizualization
# display, start_display, add_menu, add_function_to_menu = init_display()

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
    start_pnt = gp_Pnt(x_plane,0,0)

    # Specify the direction of the line
    line_dir = gp_Dir(0, direction[0], direction[1])

    #Making the line
    line_origin = Geom_Line(start_pnt, line_dir).Lin()
    line_origin = BRepBuilderAPI_MakeEdge(line_origin)
    line_origin.Build()
    line_origin = line_origin.Shape()
    return line_origin


def find_intersections(sliced_model, line_origin):
    # Finding the intersections
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform() # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution() # Get the number of intersections
    # if num_intersections != 4:
    #     return "Error: num_intersections != 4"

    # Iterate through intersections and get the points
    intersection_points = []
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        intersection_points.append(intersection_point)
    return intersection_points

# different approach but just as bad results

# def find_intersections(sliced_model, line_origin):
#     # Compute intersections between the sliced model and the line
#     section_algo = BRepAlgoAPI_Section(sliced_model, line_origin)
#     section_algo.Build()

#     # Get the generated shape containing the intersections
#     intersection_shape = section_algo.Shape()

#     # Extract intersection points from the shape
#     intersection_points = []
#     shape_explorer = TopExp_Explorer(intersection_shape, TopAbs_EDGE)
#     while shape_explorer.More():
#         edge = topods_Edge(shape_explorer.Current())
#         p1 = BRep_Tool().Pnt(BRep_Tool().FirstVertex(edge))
#         p2 = BRep_Tool().Pnt(BRep_Tool().LastVertex(edge))
#         intersection_points.append(p1)
#         intersection_points.append(p2)
#         shape_explorer.Next()

#     return intersection_points

# Definition the plane
x_plane = 10
point_on_plane = gp_Pnt(x_plane, 0, 0)  # Point on the plane
normal_to_plane = gp_Dir(1, 0, 0)  # Normal vector to the plane
plane = gp_Pln(point_on_plane, normal_to_plane)

# Load the STEP model
step_model_path = "round_bar.stp"
step_model = load_step_model(step_model_path)

# Slicing of the model - extracting the wire model
sliced_model = slice_model_with_plane(step_model, plane)# Slice the model with the plane

# Making the points and lines that will intersect the shape
direction = (0, 1)  # Direction vector
line_origin = draw_line_origin(direction)

intersection_points = find_intersections(sliced_model, line_origin)

for i in range (0, len(intersection_points)):
    # Extract coordinates
    x = intersection_points[i].X()
    y = intersection_points[i].Y()
    z = intersection_points[i].Z()

    # Print coordinates
    print(f"X coordinate: {x}")
    print(f"Y coordinate: {y}")
    print(f"Z coordinate: {z}")
    print("\n")

print(len(intersection_points))

# print(intersection_points)

# Vizualization
# display.DisplayShape(line_origin)
# display.DisplayShape(step_model, color="blue")
# display.DisplayShape(sliced_model, color="red")
# display.View_Iso()
# display.FitAll()
# start_display()
