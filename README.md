# OSTR-CONSTELATION
Coupled model using STAR-CCM+ and Serpent 2 for a HENRI-based experiment in the Oregon State TRIGA Reactor. Based on **CONSTELATION** for HENRI in TREAT ([CONSTELATION GitHub](https://github.com/warrenau/CONSTELATION)).

This project utilizes the same software, structure, and coupling method as **CONSTELATION** for TREAT, but applies it to the OSTR with a custom designed experiment. The purpose is to quantify the extent to which the coupled model **CONSTELATION** is accurate in predicting the density evolution of the helium-3 during an injection for a TREAT transient pulse and its effects on the reactor. The OSTR and the experiment designed for it will provide the data for this quantification. This project contains the code, scripts, and instructions to execute the coupled STAR-CCM+ and Serpent 2 simulation for the OSTR.

## Requirements

- Python 3 (tested using Python 3.9 from the Anaconda distribution)
- STAR-CCM+ (used version 2020.2.1 on INL HPC)
- Serpent 2 (used version 2.1.31 on INL HPC)

---
# Functions
The following section describes the functions defined and used in **CONSTELATION**.

## `position_Serpent_to_STAR(data,reference_conversion,unit_conversion)`
This function converts position values from the Serpent 2 reference frame to the STAR-CCM+ reference frame. It takes 3 inputs: `data`, `reference_conversion`, and `unit_conversion` and is defined as:
```python
data = (data-reference_conversion)*unit_conversion
return data
```
The `reference_conversion` value is the difference between the two model's reference frames. Normally, the STAR-CCM+ model is centered on the HENRI cartridge on the $x$- and $y$- axes. In the Serpent model, the HENRI cartridge has some translation from the origin as the origin is at the center of the reactor. The `unit_conversion` value addresses any discrepancy between the units of the two codes. For example, the STAR-CCM+ model may be in meters, but Serpent uses centimeters. For 2-D CFD simulations, the `unit_conversion` value can be set to zero for the dimension that does not exist in the STAR-CCM+ model.


## `SerpentHeat_to_Star_csv(detector,outfile,title)`
This function writes out Serpent 2 detector position and tally values to a *`.csv`* file for STAR-CCM+ to read, specifically for the helium-3 heating detector. The 3 inputs for this function are the `serpentTools` `Detector` ([serpentTools](https://serpent-tools.readthedocs.io/en/master/index.html) and [serpentTools DetectorReader](https://serpent-tools.readthedocs.io/en/master/examples/Detector.html)) object of interest, the *`.csv`* file to write to, and the header row of the output file.
The function includes the reference frame and unit conversion and calls the `position_Serpent_to_STAR` function as needed for the position values.


There are 12 columns in the Serpent 2 detector (Serpent manual):

1. Value index
2. Energy bin index
3. Universe bin index
4. Cell bin index
5. Material bin index
6. Lattice bin index
7. Reaction bin index
8. Z-mesh bin index
9. Y-mesh bin index
10. X-mesh bin index
11. Mean value
12. Relative statistical error

The `serpentTools` package allows for any part of the detector to be accessed. We are specifically interested with the `.tallies` portion, which is the mean value reported by Serpent. There are also $x$, $y$, and $z$ grid meshes that are printed in the detector file that the `DetectorReader` reads. These are accessed using `.grids['X']`, `.grids['Y']`, and `.grids['Z']`.

The detectors defined for passing the Serpent 2 data to STAR-CCM+ are only binned with respect to the $x$, $y$, and $z$ meshes. The `serpentTools.Detector` objects are reshaped such that the resultant array has an axis for each bin. Because the $x$ direction only has one bin, the shape of the `detector` array is ($z$-bins,$y$-bins).