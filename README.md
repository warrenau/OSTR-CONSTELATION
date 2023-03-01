# OSTR-CONSTELATION
Coupled model using STAR-CCM+ and Serpent 2 for a HENRI-based experiment in the Oregon State TRIGA Reactor. Based on **CONSTELATION** for HENRI in TREAT ([CONSTELATION GitHub](https://github.com/warrenau/CONSTELATION)).

This project utilizes the same software, structure, and coupling method as **CONSTELATION** for TREAT, but applies it to the OSTR with a custom designed experiment. The purpose is to quantify the extent to which the coupled model **CONSTELATION** is accurate in predicting the density evolution of the helium-3 during an injection for a TREAT transient pulse and its effects on the reactor. The OSTR and the experiment designed for it will provide the data for this quantification. This project contains the code, scripts, and instructions to execute the coupled STAR-CCM+ and Serpent 2 simulation for the OSTR.

## Requirements

- Python 3 (tested using Python 3.9 from the Anaconda distribution)
- STAR-CCM+ (used version 2020.2.1 on INL HPC)
- Serpent 2 (used version 2.1.31 on INL HPC)


---
# Usage
The beginning of the *`ostr_CONSTELATION_3.py`* file contains the inputs required to run the simulation.


---
# Classes
The following section describes the classes defined and used in **CONSTELATION**.

## `Serpent_ifc(object)`
This class is used to store information about the interface files used by Serpent 2. It is initialized with 4 attributes: 
```python
Top_ifc = Serpent_ifc(name,header,mesh_type,mesh)
```
These 4 attributes represent the first 4 lines written into the *`.ifc`* files that tell Serpent 2 what the file is. An additional attribute that is not required upon initialization is the `data` attribute, which is a place to store data associated with the *`.ifc`* file if necessary. The data does not need to be stored in the object when used in the `csv_to_ifc` function as the data is written out to the file.

## `STAR_csv(object)`
The `STAR_csv` class is similar to the `Serpent_ifc` class and contains information relevant to the STAR-CCM+ *`.csv`* files used to pass information to and from STAR-CCM+. It is initialized with 2 attributes:
```python
Top_csv = STAR_csv(name,header)
```
The `name` attribute is the file name used in the `python` script and the `header` attribute is the first row of the *`.csv`* file. This class also has an optional `data` attribute that can be defined later.



---
# Functions
The following section describes the functions defined and used in **CONSTELATION**.

## `wait_for_file(file,wait)`
This function takes in the file path and wait time in seconds and waits until the file exists or the wait time is exceeded. It is used a few times throughout **CONSTELATION** to make sure a file is there to be read or to wait for a file to be created during the set up. If the wait time is exceeded, there is an error that is raised to stop the program.


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


## `min_temp_fix(array)`
The cross section values used for helium-3 that have the KERMA data do not have data for helium-3 below 300K. This function fixes any temperature that is below 300K to be 300K. The input is an array of values in the form `[position,density,temperature]`. The function checks every value in the third column and makes sure it is at or above 300.0.

## `read_to_numpy(STAR_csv)`
This function reads data from a *`.csv`* file written by STAR-CCM+ and converts it to a numpy array. It uses a `pandas` function to read only the specified columns, then converts the data frame to a numpy array. The required input is a `STAR_csv` object with the file name in the `name` attribute and the desired columns in the `header` attribute.

## `csv_to_ifc(STAR_csv,Serpent_ifc)`
This function handles writing the data from a STAR-CCM+ *`.csv`* file to a Serpent 2 *`.ifc`* file. It calls both `min_temp_fix` and `read_to_numpy` within it. The inputs are the `STAR_csv` object for the STAR-CCM+ generated file being read and the `Serpent_ifc` object for the file being written to. While the incoming data has position, density, and temperature, the *`.ifc`* requires only the density and temperature data, so the function truncates the position values off when it writes to the *`.ifc`* file.

## `wait_for_file(file,wait)`
There are many places in **CONSTELATION** where the script is waiting for a file to be created so it can be read, or be used as communication about the status of the simulation. This function takes in the file name and the maximum wait time in seconds and waits until the file exists. If the file does not exist at the end of the wait time, and error is raised.

## `com_check_digit(line,sig_notdigit)`
For a reason that may never be determined, sometimes the contents of the *`com.out`* file are removed. This may be caused by the server, the simulation, both, or neither. This function checks that the contents of the file are able to be converted into an integer so that the simulation is not ended by an error trying to convert nothing to an integer. The inputs are the line that was read in from the *`com.out`* file and the false signal to give the output variable if the contents cannot be read properly. This false signal has its own place in the `if` loop that interprets the signal, which continues the simulation as if the signal was to resume current iteration, but it prints out the number provided in the `sig_notdigit` input.