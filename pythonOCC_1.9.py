# calculating second moemnt of enertia half succesfully

import math
from OCC.Display.SimpleGui import init_display
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Line
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve


# Preparing the vizualization
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
    negative_limiter = gp_Pnt(0, - direction[0], - direction[1])
    positive_limiter = gp_Pnt(0, 9999 * direction[0], 9999 * direction[1]) # needs sizing based on the size of the wire!
    line_origin = BRepBuilderAPI_MakeEdge(negative_limiter, positive_limiter)
    line_origin.Build()
    line_origin = line_origin.Shape()
    return line_origin

def find_intersections_in(sliced_model, line_origin): # Find the points on the inner shell
    # Finding the intersections
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform() # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution() # Get the number of intersections
    if num_intersections != 2:
        return "Error: num_intersections != 2"

    # Iterate through intersections and get the points
    points_on_plane = []
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        points_on_plane.append(intersection_point)
    if (math.sqrt(points_on_plane[0].Y() ** 2 + points_on_plane[0].Z() ** 2) < math.sqrt(points_on_plane[1].Y() ** 2 + points_on_plane[1].Z() ** 2)): #input the check of distances! And save acordingly smaller value
        intersection_points_in.append(points_on_plane[0])
    else:
        intersection_points_in.append(points_on_plane[1])
    return intersection_points_in

def find_intersections_out(sliced_model, line_origin): # Find the points on the outer shell
    # Finding the intersections
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform() # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution() # Get the number of intersections
    if num_intersections != 2:
        return "Error: num_intersections != 2"

    # Iterate through intersections and get the points
    points_on_plane = []
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        points_on_plane.append(intersection_point)
    if (math.sqrt(points_on_plane[0].Y() ** 2 + points_on_plane[0].Z() ** 2) > math.sqrt(points_on_plane[1].Y() ** 2 + points_on_plane[1].Z() ** 2)): #input the check of distances! And save acordingly bigger value
        intersection_points_out.append(points_on_plane[0])
    else:
        intersection_points_out.append(points_on_plane[1])
    return intersection_points_out



# Definition the plane
x_plane = 800
point_on_plane = gp_Pnt(x_plane, 0, 0)  # Point on the plane
normal_to_plane = gp_Dir(1, 0, 0)  # Normal vector to the plane
plane = gp_Pln(point_on_plane, normal_to_plane)

# Load the STEP model
step_model_path = "Rechteckrohr_verjuengt_Volumen.stp"
step_model = load_step_model(step_model_path)

# Slicing of the model - extracting the wire model
sliced_model = slice_model_with_plane(step_model, plane)# Slice the model with the plane


intersection_points_in = [] # Declare empty list for inner shell
intersection_points_out = [] # Declare empty list for outer shell
desired_num_points = 100
for i in range(0, desired_num_points):
    angle_pich = (2 * math.pi) / desired_num_points
    cur_angle = i * angle_pich
    direction =  (math.sin(cur_angle), math.cos(cur_angle))
    line_origin = draw_line_origin(direction)
    intersection_points_in = find_intersections_in(sliced_model, line_origin)
    intersection_points_out = find_intersections_out(sliced_model, line_origin)

area = 0
second_moment_area = 0
for i in range (0, len(intersection_points_in) - 1): # Calculating areas of triangles using vertexes - formula half of sum of things #google it
    # using two triangles at a time 
    tri_area_1 = (1/2)*abs(((intersection_points_in[i].Y()*(intersection_points_in[i+1].Z() - (intersection_points_out[i].Z()))) + (intersection_points_in[i+1].Y()*((intersection_points_out[i].Z()) - intersection_points_in[i].Z())) + (intersection_points_out[i].Y()*(intersection_points_in[i].Z() - intersection_points_in[i+1].Z()))))
    area += tri_area_1

    tri_area_2 = (1/2)*abs(((intersection_points_in[i+1].Y()*(intersection_points_out[i+1].Z() - (intersection_points_out[i].Z()))) + (intersection_points_out[i+1].Y()*((intersection_points_out[i].Z()) - intersection_points_in[i+1].Z())) + (intersection_points_out[i].Y()*(intersection_points_in[i+1].Z() - intersection_points_out[i+1].Z()))))
    area += tri_area_2

    # calculating the lenghts lenthg of the triangls base - first triangle
    b = math.sqrt( ((intersection_points_in[i+1].Y() - intersection_points_in[i].Y()) ** 2) + ((intersection_points_in[i+1].Z() - intersection_points_in[i].Z()) ** 2) )
    
    # calculating the heitght of triangle
    numerator = abs((intersection_points_in[i+1].Y() - intersection_points_in[i].Y()) * (intersection_points_in[i].Z() - intersection_points_out[i+1].Z()) - (intersection_points_in[i].Y() - intersection_points_out[i].Y()) * (intersection_points_in[i+1].Z() - intersection_points_in[i].Z()))
    denominator = math.sqrt((intersection_points_in[i+1].Y() - intersection_points_in[i].Y()) ** 2 + (intersection_points_in[i+1].Z() - intersection_points_in[i].Z()) ** 2)
    
    h = numerator / denominator # Calculates the distance between a line defined by two points (in (i) and in (i+1)) and a third point out (i)

    second_moment_area_no_steiner = b * (h ** (3/12))

    # calculating the coordinated of the centorid of triangle
    centroid_triangle = gp_Pnt(x_plane, (intersection_points_in[i].Y() + intersection_points_in[i+1].Y() + intersection_points_out[i].Y()) / 3, (intersection_points_in[i].Z() + intersection_points_in[i+1].Z() + intersection_points_out[i].Z()) / 3)

    # steiner is second moment of area + area times distance to center ** 2
    second_moment_area_steiner = second_moment_area_no_steiner + (tri_area_1 * (centroid_triangle.Y() ** 2 + centroid_triangle.Z() ** 2))

    # sum of all triangles second moment of enertia
    second_moment_area += second_moment_area_steiner


print('area:')
print(area)

print('second_moment_area:')
print(second_moment_area)

# for point in intersection_points_in:
#     display.DisplayShape(point, color="black")

# for point in intersection_points_out:
#     display.DisplayShape(point, color="green")

# Vizualization
# display.DisplayShape(line_origin)
# display.DisplayShape(step_model, color="blue")
# display.DisplayShape(sliced_model, color="red")
# display.View_Iso()
# display.FitAll()
# start_display()
