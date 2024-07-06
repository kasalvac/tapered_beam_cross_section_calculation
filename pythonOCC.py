# managed to make working lines

import math
from OCC.Display.SimpleGui import init_display
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.TopoDS import topods_Face, TopoDS_Compound, TopoDS_Iterator
from OCC.Core.Geom import Geom_Line
from OCC.Core.GeomAPI import GeomAPI_IntCS
from OCC.Core.BRep import BRep_Tool

# Starting the vizualization
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

def extract_faces(shape):
    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while face_explorer.More():
        face = topods_Face(face_explorer.Current())
        faces.append(face)
        face_explorer.Next()
    return faces

def create_mesh(shape):
    mesh = BRepMesh_IncrementalMesh(shape, 0.1)  # Adjust the deflection parameter if trouble :D 
    mesh.Perform()
    return mesh

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



# Definition the plane
x_plane = 10
point_on_plane = gp_Pnt(x_plane, 0, 0)  # Point on the plane
normal_to_plane = gp_Dir(1, 0, 0)  # Normal vector to the plane
plane = gp_Pln(point_on_plane, normal_to_plane)

 # Load the STEP model
step_model_path = "Fluegelhuelle_Test3.stp"
step_model = load_step_model(step_model_path)

# Slicing of the model and extracting the wire model
sliced_model = slice_model_with_plane(step_model, plane)# Slice the model with the plane
faces = extract_faces(sliced_model)# Extract faces from the sliced model
mesh = create_mesh(sliced_model)# Create a mesh from the sliced model


# Making the points and lines that will intersect the shape
direction = (1, 1)  # Direction vector
line_origin = draw_line_origin(direction)

# display.DisplayShape(line_origin, color="black")

# display.DisplayShape(step_model, color="blue")
# display.DisplayShape(sliced_model, color="red")

shape_iterator = TopoDS_Iterator(step_model)
while shape_iterator.More():
    subshape = shape_iterator.Value()
    # Process the subshape as needed
    print(subshape.ShapeType())  # This will print the type of the subshape
    shape_iterator.Next()

shape_iterator = TopoDS_Iterator(sliced_model)
while shape_iterator.More():
    subshape = shape_iterator.Value()
    # Process the subshape as needed
    print(subshape.ShapeType())  # This will print the type of the subshape
    shape_iterator.Next()


def extract_edge_curve(edge):
    """Extracts the geometric curve from an edge."""
    curve, _, _ = BRep_Tool.Curve(edge)  # Retrieve the geometric curve of the edge
    return curve

def extract_wire_function(wire):
    """Extracts the functions describing the edges of a wire."""
    edge_functions = []
    explorer = TopExp_Explorer(wire, TopAbs_EDGE)  # Iterate over the edges of the wire
    while explorer.More():
        edge = explorer.Current()
        curve = extract_edge_curve(edge)
        edge_functions.append(curve)
        explorer.Next()
    return edge_functions

# Assuming 'my_wire' is your TopoDS_Wire
# Extract the functions describing the edges of the wire
wire_functions = extract_wire_function(sliced_model)
for idx, edge_function in enumerate(wire_functions, start=1):
    print(f"Edge {idx} function:", edge_function)
    

# display.View_Iso()
# display.FitAll()
start_display()
