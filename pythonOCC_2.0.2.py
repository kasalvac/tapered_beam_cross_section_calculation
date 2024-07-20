# calculating moments of inertia correctly #thanksgrandpa 
# not working for big number of points because of security check
#chceck skipped

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
    # if num_intersections != 2:
    #     return "Error: num_intersections != 2"

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
    # if num_intersections != 2:
    #     return "Error: num_intersections != 2"

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
x_plane = 1000
point_on_plane = gp_Pnt(x_plane, 0, 0)  # Point on the plane als othe center of the cross section
normal_to_plane = gp_Dir(1, 0, 0)  # Normal vector to the plane
plane = gp_Pln(point_on_plane, normal_to_plane)

# Load the STEP model
step_model_path = "Rechteckrohr_verjuengt_Volumen.stp"
step_model = load_step_model(step_model_path)

# Slicing of the model - extracting the wire model
sliced_model = slice_model_with_plane(step_model, plane)# Slice the model with the plane


intersection_points_in = [] # Declare empty list for inner shell
intersection_points_out = [] # Declare empty list for outer shell
desired_num_points = 1000
for i in range(0, desired_num_points):
    angle_pich = (2 * math.pi) / desired_num_points
    cur_angle = i * angle_pich
    direction =  (math.sin(cur_angle), math.cos(cur_angle))
    line_origin = draw_line_origin(direction)
    intersection_points_in = find_intersections_in(sliced_model, line_origin)
    intersection_points_out = find_intersections_out(sliced_model, line_origin)

area = 0
moment_of_inertia_Y = 0
moment_of_inertia_Z = 0
for i in range (0, len(intersection_points_in) - 1): # Calculating areas of triangles using vertexes - formula half of sum of things #google it
    # using two triangles at a time 

    # first triangle Area
    tri_area_1 = (1/2)*abs(((intersection_points_in[i].Y()*(intersection_points_in[i+1].Z() - (intersection_points_out[i].Z()))) + (intersection_points_in[i+1].Y()*((intersection_points_out[i].Z()) - intersection_points_in[i].Z())) + (intersection_points_out[i].Y()*(intersection_points_in[i].Z() - intersection_points_in[i+1].Z()))))
    area += tri_area_1

    # second triangle Area
    tri_area_2 = (1/2)*abs(((intersection_points_in[i+1].Y()*(intersection_points_out[i+1].Z() - (intersection_points_out[i].Z()))) + (intersection_points_out[i+1].Y()*((intersection_points_out[i].Z()) - intersection_points_in[i+1].Z())) + (intersection_points_out[i].Y()*(intersection_points_in[i+1].Z() - intersection_points_out[i+1].Z()))))
    area += tri_area_2

    # first triangle moments of inertia to the Y axis (converted to be X axis)
    # sorting the points based on Z coordinate (distance to axis)
    points_1 = [intersection_points_in[i], intersection_points_in[i+1], intersection_points_out[i]]
    sorted_points_1 = sorted(points_1, key=lambda p: p.Z())
    
    # referencing the coordinated to point closest to axis
    Bx_1 = (sorted_points_1[1].Y() - sorted_points_1[0].Y())
    By_1 = (sorted_points_1[1].Z() - sorted_points_1[0].Z())
    Cx_1 = (sorted_points_1[2].Y() - sorted_points_1[0].Y())
    Cy_1 = (sorted_points_1[2].Z() - sorted_points_1[0].Z())

    # trinagle has to be split into two via a parallel line to axis going through the middle point
    Dx_1 = Cx_1 * (By_1/Cy_1) # coordinate of the point on the parallel line
    b_2 = abs(Dx_1 - Bx_1) # calculating lenght of the base of both triangles
    Y0_1 = (b_2 / 12) * (By_1 ** 3 + (Cy_1 - By_1) ** 3) # calculating the moment of inertia of triangle to the split line
    t_2 = (By_1 + Cy_1) / 3 # calculating the distance of center of mass to poit closest to axis
    Yt_1 = Y0_1 - tri_area_1 * ((By_1 - t_2) ** 2) # moment of inertia to thhe center of mass
    Ys_1 = Yt_1 + tri_area_1 * ((t_2 + sorted_points_1[0].Z()) ** 2) #moment of inertia to the centerpoint
    moment_of_inertia_Y += Ys_1

    # second triangle moments of inertia to the Y axis (converted to be X axis)
    # sorting the points based on Z coordinate (distance to axis)
    points_2 = [intersection_points_in[i+1], intersection_points_out[i], intersection_points_out[i+1]]
    sorted_points_2 = sorted(points_2, key=lambda p: p.Z())
    
    # referencing the coordinated to point closest to axis
    Bx_2 = (sorted_points_2[1].Y() - sorted_points_2[0].Y())
    By_2 = (sorted_points_2[1].Z() - sorted_points_2[0].Z())
    Cx_2 = (sorted_points_2[2].Y() - sorted_points_2[0].Y())
    Cy_2 = (sorted_points_2[2].Z() - sorted_points_2[0].Z())

    # trinagle has to be split into two via a parallel line to axis going through the middle point
    Dx_2 = Cx_2 * (By_2/Cy_2) # coordinate of the point on the parallel line
    b_2 = abs(Dx_2 - Bx_2) # calculating lenght of the base of both triangles
    Y0_2 = (b_2 / 12) * (By_2 ** 3 + (Cy_2 - By_2) ** 3) # calculating the moment of inertia of triangle to the split line
    t_2 = (By_2 + Cy_2) / 3 # calculating the distance of center of mass to poit closest to axis (might be wrong!!!!!!)
    Yt_2 = Y0_2 - tri_area_2 * ((By_2 - t_2) ** 2) # moment of inertia to thhe center of mass
    Ys_2 = Yt_2 + tri_area_2 * ((t_2 + sorted_points_2[0].Z()) ** 2) #moment of inertia to the centerpoint
    moment_of_inertia_Y += Ys_2
    


print('area:')
print(area)

print('moment_of_inertia_Y:')
print(moment_of_inertia_Y)

# Vizualization
# display.DisplayShape(line_origin)
# display.DisplayShape(step_model, color="blue")
# display.DisplayShape(sliced_model, color="red")
# display.View_Iso()
# display.FitAll()
# start_display()
