# Working visualization of the slice

from OCC.Display.SimpleGui import init_display
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.TopoDS import topods_Face

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

# Definition the plane
point_on_plane = gp_Pnt(1000, 0, 0)  # Point on the plane
normal_to_plane = gp_Dir(1, 0, 0)  # Normal vector to the plane
plane = gp_Pln(point_on_plane, normal_to_plane)

# Load the STEP model
step_model_path = "Rechteckrohr_verjuengt_Volumen.stp"
step_model = load_step_model(step_model_path)

# Slice the model with the plane
sliced_model = slice_model_with_plane(step_model, plane)

# Extract faces from the sliced model
faces = extract_faces(sliced_model)

# Create a mesh from the sliced model
mesh = create_mesh(sliced_model)

# Visualize the result
display, start_display, add_menu, add_function_to_menu = init_display()

display.DisplayShape(step_model, color="blue")
display.DisplayShape(sliced_model, color="red")

display.FitAll()
start_display()
