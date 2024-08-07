# calculating moments of inertia correctly #thanksgrandpa 
# not working for big number of points because of security check
# chceck skipped
# adding center of mass calculation
# making it calculate along the wing box

import math
from OCC.Display.SimpleGui import init_display
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Line
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
import pandas as pd


# Preparing the vizualization
# display, start_display, add_menu, add_function_to_menu = init_display()

def load_step_model(file_path):
    """
    Loads a STEP file and returns the geometric shape.

    Parameters:
    file_path (str): The path to the STEP file to be loaded.

    Returns:
    TopoDS_Shape: The shape object extracted from the STEP file.
    """
    reader = STEPControl_Reader()
    reader.ReadFile(file_path)
    reader.TransferRoots()
    return reader.Shape()

def slice_model_plane_par_x(model, x_coordinate):
    """
    Slice a 3D model with a plane parallel to the YZ-plane at a given x-coordinate.

    Parameters:
    model : The 3D model to be sliced.
    x_coordinate : float
        The x-coordinate at which the slicing plane is defined.

    Returns:
    section_shape : The cross-section shape resulting from the slicing operation.
    """
    # Define the plane
    point_on_plane = gp_Pnt(x_coordinate, 0, 0)  # Point on the plane, also the center of the cross-section
    normal_to_plane = gp_Dir(1, 0, 0)  # Normal vector to the plane
    plane = gp_Pln(point_on_plane, normal_to_plane)

    # Slice the model with the defined plane
    section_algo = BRepAlgoAPI_Section(model, plane)
    section_algo.Build()

    # Return the resulting cross-section shape
    return section_algo.Shape()

def draw_line_origin(direction):
    """
    Creates a line starting from the origin (0, 0, 0) extending in the specified direction.
    
    Parameters:
    direction (list or tuple): A list or tuple with two elements specifying the Y and Z 
                               direction components of the line.
    
    Returns:
    TopoDS_Shape: The shape of the line created.
    """
    # Create the starting point at the origin
    start_pnt = gp_Pnt(0, 0, 0)
    
    # Specify the direction of the line
    line_dir = gp_Dir(0, direction[0], direction[1])
    
    # Create the line using the start point and direction
    geom_line = Geom_Line(start_pnt, line_dir).Lin()
    
    # Define the points that limit the line (from a negative to a positive extreme)
    negative_limiter = gp_Pnt(0, -direction[0], -direction[1])
    positive_limiter = gp_Pnt(0, 9999 * direction[0], 9999 * direction[1])  # Needs sizing based on the size of the wire
    
    # Make an edge from the limiting points
    line_edge = BRepBuilderAPI_MakeEdge(negative_limiter, positive_limiter)
    line_edge.Build()
    
    # Get the shape of the line
    line_shape = line_edge.Shape()
    
    return line_shape

def find_intersections_in(sliced_model, line_origin):
    """
    Find the intersection points between a sliced model and a line.

    Parameters:
    sliced_model (TopoDS_Shape): The sliced model to check for intersections.
    line_origin (TopoDS_Shape): The line used to find intersections with the sliced model.

    Returns:
    list: A list of intersection points on the inner shell.
    """
    # Initialize the intersection calculator with the sliced model and the line
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform()  # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution()  # Get the number of intersections

    # List to store the intersection points
    points_on_plane = []

    # Iterate through the intersections and get the points
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        points_on_plane.append(intersection_point)

    # Determine the closer intersection point based on Y and Z coordinates
    if math.sqrt(points_on_plane[0].Y() ** 2 + points_on_plane[0].Z() ** 2) < math.sqrt(points_on_plane[1].Y() ** 2 + points_on_plane[1].Z() ** 2):
        intersection_points_in.append(points_on_plane[0])
    else:
        intersection_points_in.append(points_on_plane[1])

    return intersection_points_in

def find_intersections_out(sliced_model, line_origin):
    """
    Find the intersection points on the outer shell of a given model.

    Parameters:
    - sliced_model: The model to be intersected, represented as a TopoDS_Shape.
    - line_origin: The reference line or point used for finding intersections, represented as a TopoDS_Shape.

    Returns:
    - intersection_points_out: A list containing the intersection point on the outer shell of the model.
    """

    # Perform the intersection calculation
    extrema_calculator = BRepExtrema_DistShapeShape(sliced_model, line_origin)
    extrema_calculator.Perform()  # Perform the calculation to find intersections
    num_intersections = extrema_calculator.NbSolution()  # Get the number of intersections

    # Initialize a list to store points on the plane
    points_on_plane = []
    
    # Iterate through intersections and collect the points
    for i in range(1, num_intersections + 1):
        extrema_point = extrema_calculator.PointOnShape1(i)
        intersection_point = gp_Pnt(extrema_point.X(), extrema_point.Y(), extrema_point.Z())
        points_on_plane.append(intersection_point)

    # Determine the point that lies further from the origin in the YZ plane
    if (math.sqrt(points_on_plane[0].Y() ** 2 + points_on_plane[0].Z() ** 2) > math.sqrt(points_on_plane[1].Y() ** 2 + points_on_plane[1].Z() ** 2)): #input the check of distances! And save acordingly bigger value
        intersection_points_out.append(points_on_plane[0])
    else:
        intersection_points_out.append(points_on_plane[1])

    return intersection_points_out

def calculate_triangle_area(p1, p2, p3):
    """
    Calculate the area of a triangle given three points.
    
    Parameters:
    p1, p2, p3 (gp_Pnt): Points representing the vertices of the triangle.
    
    Returns:
    float: The area of the triangle.
    """
    x1, y1, z1 = p1.X(), p1.Y(), p1.Z()
    x2, y2, z2 = p2.X(), p2.Y(), p2.Z()
    x3, y3, z3 = p3.X(), p3.Y(), p3.Z()
    
    # Calculate vectors from p1 to p2 and from p1 to p3
    vector1 = (x2 - x1, y2 - y1, z2 - z1)
    vector2 = (x3 - x1, y3 - y1, z3 - z1)
    
    # Calculate the cross product of the two vectors
    cross_product = (
        vector1[1] * vector2[2] - vector1[2] * vector2[1],
        vector1[2] * vector2[0] - vector1[0] * vector2[2],
        vector1[0] * vector2[1] - vector1[1] * vector2[0]
    )
    
    # Calculate the magnitude of the cross product vector
    cross_product_magnitude = (cross_product[0]**2 + cross_product[1]**2 + cross_product[2]**2)**0.5
    
    # The area of the triangle is half the magnitude of the cross product of the vectors
    area = 0.5 * cross_product_magnitude
    
    return area

def calculate_triangle_moment_of_inertia_Y(p1, p2, p3):
    """
    Calculate the moment of inertia of a triangle defined by three points about a specified axis.

    Parameters:
    p1, p2, p3 (gp_Pnt): Points representing the vertices of the triangle.

    Returns:
    float: The moment of inertia of the triangle about the specified axis.
    """
    # Assuming tri_area is provided or calculated elsewhere
    tri_area = calculate_triangle_area(p1, p2, p3)

    # List of points
    points = [p1, p2, p3]

    # Sort points based on the specified axis
    sorted_points = sorted(points, key=lambda p: p.Z())

    # for i, point in enumerate(sorted_points):
    #     print(f"Point {i+1}: ({point.X()}, {point.Y()}, {point.Z()})")

    # Referencing the coordinates to the point closest to the axis
    By = (sorted_points[1].Y() - sorted_points[0].Y())
    Bz = (sorted_points[1].Z() - sorted_points[0].Z())
    Cy = (sorted_points[2].Y() - sorted_points[0].Y())
    Cz = (sorted_points[2].Z() - sorted_points[0].Z())

    # Triangle has to be split into two via a parallel line to axis going through the middle point
    Dy = Cy * (Bz / Cz) if Cz != 0 else 0  # Coordinate of the point on the parallel line
    b = abs(Dy - By)  # Calculating length of the base of both triangles

    # Moment of inertia calculations (adjusted for the correct formulas)
    Y0 = (b / 12) * (Bz ** 3 + (Cz - Bz) ** 3)  # Moment of inertia of triangle to the split line
    t = (Bz + Cz) / 3  # Distance of the center of mass to point closest to axis
    Yt = Y0 - tri_area * ((Bz - t) ** 2)  # Moment of inertia to the center of mass
    Ys = Yt + tri_area * ((t + sorted_points[0].Z()) ** 2)  # Moment of inertia to the center point

    return Ys

def calculate_triangle_moment_of_inertia_Z(p1, p2, p3):
    """
    Calculate the moment of inertia of a triangle defined by three points about a specified axis.

    Parameters:
    p1, p2, p3 (gp_Pnt): Points representing the vertices of the triangle.

    Returns:
    float: The moment of inertia of the triangle about the specified axis.
    """
    # Assuming tri_area is provided or calculated elsewhere
    tri_area = calculate_triangle_area(p1, p2, p3)

    # List of points
    points = [p1, p2, p3]

    # Sort points based on the specified axis
    sorted_points = sorted(points, key=lambda p: p.Y())

    # for i, point in enumerate(sorted_points):
    #     print(f"Point {i+1}: ({point.X()}, {point.Y()}, {point.Z()})")

    # Referencing the coordinates to the point closest to the axis
    By = (sorted_points[1].Y() - sorted_points[0].Y())
    Bz = (sorted_points[1].Z() - sorted_points[0].Z())
    Cy = (sorted_points[2].Y() - sorted_points[0].Y())
    Cz = (sorted_points[2].Z() - sorted_points[0].Z())

    # Triangle has to be split into two via a parallel line to axis going through the middle point
    Dz = Cz * (By / Cy) if Cy != 0 else 0  # Coordinate of the point on the parallel line
    b = abs(Dz - Bz)  # Calculating length of the base of both triangles

    # Moment of inertia calculations (adjusted for the correct formulas)
    Y0 = (b / 12) * (By ** 3 + (Cy - By) ** 3)  # Moment of inertia of triangle to the split line
    t = (By + Cy) / 3  # Distance of the center of mass to point closest to axis
    Yt = Y0 - tri_area * ((By - t) ** 2)  # Moment of inertia to the center of mass
    Ys = Yt + tri_area * ((t + sorted_points[0].Y()) ** 2)  # Moment of inertia to the center point

    return Ys

# Open the *.txt-file with coordinated where to colaculate
sensor_info = pd.read_csv('Sensor_Positions_Vaclav_fixed.txt', delimiter=',', header=None)
sensor_info.columns = ['ID', 'X', 'Y', 'Z']
sensor_info = sensor_info.astype({"ID": int, "X": float, "Y": float, "Z": float})

# Load the STEP model
step_model_path = "Tapered-Beam-Volume.stp"
step_model = load_step_model(step_model_path)

sensor_info['distance'] = 0.0
sensor_info['inertiaZ'] = 0.0
sensor_info['inertiaY'] = 0.0

# Loop through each value in column with X values
for index, value in sensor_info['X'].items():
    # Perform all the calculations calculation needs to be more pretty in the future

    x_plane = value

    # Slicing of the model - extracting the wire model
    sliced_model = slice_model_plane_par_x(step_model, x_plane)# Slice the model with the plane

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
    cent_mass_Y_prepare = 0
    cent_mass_Z_prepare = 0
    moment_of_inertia_Y = 0
    moment_of_inertia_Z = 0

    for i in range (0, len(intersection_points_in) - 1): # Calculating areas of triangles using vertexes - formula half of sum of things #google it
        # using two triangles at a time 
        # using two types of indexes, 1 and 2 for first a nd second triangle in the loop and Y and Z for the axis which I am calculating the moment of inertia to

        # first triangle Area
        tri_area_1 = calculate_triangle_area(intersection_points_in[i], intersection_points_in[i+1], intersection_points_out[i])
        area += tri_area_1

        # second triangle Area
        tri_area_2 = calculate_triangle_area(intersection_points_in[i+1], intersection_points_out[i], intersection_points_out[i+1])
        area += tri_area_2

        # calculation of center of mass
        #starting by finding the centroid of the triangles
        tri_centr_Y_1 = (intersection_points_in[i].Y() + intersection_points_in[i+1].Y() + intersection_points_out[i].Y())/3
        tri_centr_Z_2 = (intersection_points_in[i+1].Y() + intersection_points_out[i+1].Y() + intersection_points_out[i].Y())/3
        tri_centr_Y_1 = (intersection_points_in[i].Z() + intersection_points_in[i+1].Z() + intersection_points_out[i].Z())/3
        tri_centr_Z_2 = (intersection_points_in[i+1].Z() + intersection_points_out[i+1].Z() + intersection_points_out[i].Z())/3
        # precalculating the coordinates (needs to be divided by total area in the end)
        cent_mass_Y_prepare += tri_area_1 * tri_centr_Y_1 + tri_area_2 * tri_centr_Z_2
        cent_mass_Z_prepare += tri_area_1 * tri_centr_Y_1 + tri_area_2 * tri_centr_Z_2

        # Using the funtion to calculate the moment of inertia for the first triangle
        moment_of_inertia_Y += calculate_triangle_moment_of_inertia_Y(intersection_points_in[i], intersection_points_in[i+1], intersection_points_out[i])

        # Using the funtion to calculate the moment of inertia for the second triangle
        moment_of_inertia_Y += calculate_triangle_moment_of_inertia_Y(intersection_points_in[i+1], intersection_points_out[i], intersection_points_out[i+1])

        # Using the funtion to calculate the moment of inertia for the first triangle
        moment_of_inertia_Z += calculate_triangle_moment_of_inertia_Z(intersection_points_in[i], intersection_points_in[i+1], intersection_points_out[i])

        # Using the funtion to calculate the moment of inertia for the second triangle
        moment_of_inertia_Z += calculate_triangle_moment_of_inertia_Z(intersection_points_in[i+1], intersection_points_out[i], intersection_points_out[i+1])



    # finalizing the calculation of center of mass has to be done outside the loop because total area is requiered
    cent_mass_Y = cent_mass_Y_prepare / area
    cent_mass_Z = cent_mass_Z_prepare / area

    # finalizing the calculation of distance to neutral fiber
    distance_neutral_fiber = math.sqrt((cent_mass_Y - sensor_info.at[index, 'Y'])**2 + (cent_mass_Z - sensor_info.at[index, 'Z'])**2)


    sensor_info.at[index, 'distance'] = distance_neutral_fiber
    sensor_info.at[index, 'inertiaZ'] = moment_of_inertia_Z
    sensor_info.at[index, 'inertiaY'] = moment_of_inertia_Y
    

print('sensor info:')
print(sensor_info)
