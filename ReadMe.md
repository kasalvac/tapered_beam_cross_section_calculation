# tapered_beam_cross_section_calculation
this script utilizes PythonOCC to load a stp model and slice it along its X axis. 
Using custom triangulation method calculates:
    area of scross section
    center of mass
    moments of inertia to axis Y & Z
    polar moment of inertia

just with with 1000 points the error is less than 1% and calculation takes around 500 ms for more information go to:
    Analysis of the algorithm's performance.png

for description of the whole algorihm go to:
    Calculation of geometric values for shape and load sensing from CAD models_kasal_presentation.pptx

