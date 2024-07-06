from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Extend.DataExchange import read_step_file

my_shape = read_step_file('Rechteckrohr_verjuengt_Volumen.stp')
prop = GProp_GProps()
tolerance = 1e-5 # Adjust to your liking
volume = brepgprop_VolumeProperties(my_shape, prop, tolerance)
print(volume)