



---
# Prepping OSTR Serpent Model
- running *`TRIGA_05tube_D5_void`* on INL HPC 6 nodes, 48 cores each
    - $k_{eff}=1.02308$ with 

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | 2.0955  |
    | sa  | 2.0955  |
    | sh  | -4.953  |
    | reg | 2.0974  |

- trying putting rods back to default values (fully inserted, I think)

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | -19.05  |
    | sa  | -19.05  |
    | sh  | -19.05  |
    | reg | -18.5928|

    - $k_{eff}=0.97465$

- trying setting the rods just below the default positions defined in the input file (where the trans cards are 0)

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | -2.0955 |
    | sa  | -2.0955 |
    | sh  | -4.953  |
    | reg | -2.0974 |

    - $k_{eff}=1.01252$

- lets try moving the rods further down

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | -5 |
    | sa  | -5 |
    | sh  | -8  |
    | reg | -5 |

    - $k_{eff}=1.00218$

- lets try moving the rods down a little bit more

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | -6 |
    | sa  | -6 |
    | sh  | -9  |
    | reg | -6 |

    - $k_{eff}=0.99879$

- lets move the rods a little bit back up

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | -5.5 |
    | sa  | -5.5 |
    | sh  | -8.5  |
    | reg | -5.5 |

    - $k_{eff}=1.00045$

- lets try moving the shim rod further in just a little bit

    | Rod | z-trans |
    | :---: | :---: |
    | tr  | -5.5 |
    | sa  | -5.5 |
    | sh  | -9  |
    | reg | -5.5 |

    - $k_{eff}=1.00007$

- Began setting up directory on HPC to run coupled sims:
    - *`/xs`*: cross section data
    - *`oma.xsdata`*: references to cross section data
    - ostr serpent model
    - still need *`.ifc`* files

- Ran another criticality sim with updated geometry and void in air gap as well.
    - $k_{eff}=1.00007$
- Will run transient source generation with the rod positions as they are and with the voids.
    - TRIGA power is set to: 2200 MW (from Dr. Reese)
    - ran, but I misspelled setsrc. rerunning with 2000MW power and correct spelling.
    - ran and I have a source file to start a transient simulation from!

- Going to move experiment to different position in core: G8
    - steady state results with experiment in G8 made of aluminum vs no experiment in the core show a reactivity change of -$0.11, which is less than $0.25, so the reactor does not need to be re-calibrated.



---
# First Coupled Attempt

## File Structure

```
|-- Archive/
|-- ExtractedData/
|   |-- He3Data_table.csv
|-- ostr_CONSTELATION_3.py
|-- functions.py
|-- ostr-coupled-3e-1mm-poly.sim
|-- load_dataTop.java
|-- TRIGA_D5
|-- Source.live
|-- Source.main
|-- Source.prec
|-- Source.precpoints
|-- STAR_job.sh
|-- Serpent_job.sh
```

## INL HPC Settings

### Serpent Model
- will first try 25 nodes
    - the *`source.live`* file is about 14GB, compared to 55GB for the TREAT model
    - the TREAT model uses 85 Nodes and 16TB of memory
    - if the *`source.live`* file is an indication in a linear way, the TRIGA model will need 4.4TB of memory, so 25 nodes is a good starting point. It will probably need more, but I don't know how much more.
- 25 nodes was not enough, going to try 35 nodes
- 35 nodes was also not enough, going to try 50 nodes
- 50 nodes was not enough, trying 60 nodes.
- 60 nodes was not enough, trying 70 nodes.
- 70 nodes was not enough, trying 80 nodes.
    - also had a problem at line 188 in *`ostr_CONSTELATION_3.py`* file. no *`com.out`* file, but I mightve deleted it before looking at the terminal output.
- 80 nodes was not enough, trying 90 nodes.
- 90 nodes was not enough, trying 100 nodes.
- 100 nodes was not enough, trying 110 nodes.
- 110 nodes was not enough, trying 120 nodes.
- 120 nodes was not enough, trying 130 nodes.
- 130 nodes was not enough, trying 140 nodes. (there are more error messages at the end of the output file now, so hopefully we are getting closer.)
- 140 nodes was not enough, trying 150 nodes.
- 150 nodes was not enough, trying 160 nodes.
- 160 nodes was not enough, trying 170 nodes.
- 170 nodes was not enough, trying 180 nodes.

replaced all fuel with one material m1507, trying 50 nodes
- error due to detector file name being written wrong in the code. fixed and am trying again
- error due to variables not defined in function file, specifically with `SerpentHeat_to_Star_csv` function. fixed and trying again.
- *`_res.m`* file was not created. Im going to comment that part out from the code to get it to run and troubleshoot the reactivity tracking later.
- found typo in heat unit conversion: fixed and restarted sim


March 31, 2023:
- got error after reading in *`HE3.ifc`*: 
```
Fatal error in function SetIFCTMSLimits:

Material temperature 300.000000 below TMS minorant for material helium3
```
- looking at the two files, *`HE3.ifc`* and *`He3Data_table.csv`*, the *`.ifc`* has the correct values in the correct columns (density, temperature). However, the temperatures are all 300K even though in the *`.csv`* file they are ~~302K~~ 294-297K (The initial file is 302K, but the second file that was generated after the first star cycle had lower temperatures in it). ~~This means that the temp fix function is working too well.~~ The density conversion appears to be working correctly. I may increase the number of decimals reported because the density only has one significant digit a the moment with the low starting density.
- changed `min_temp_fix` function to set min temp to 301K instead of 300K. Maybe the precision was causing a problem? Also increased the decimals reported from `"%1.6f"` to `"%1.9f"` to give more decimals for the density value.

April 05, 2023:
```
Fatal error in function SetIFCTMSLimits:

Material temperature 301.000000 below TMS minorant for material helium3

Simulation aborted.
```
- reached out to Cole. I don't know how to fix this one right now. I will keep looking into it though.
- Dr. Mignot scrolled further through some slides I also found last week and found the `tft` input for `mat` cards to set the TMS temperature limits.
- going to rerun source sim with updated model with only one fuel material, TMS limits, etc. Cole mentioned that the steady state / source run sets the temperature limits, then I realized that I had made a lot of changes to the model since I ran the source simulation and it would prolly be a good idea to run it. I also used the *`.ifc`* file to set the density of the helium-3. Hopefully it works and is happy with the new fuel load.

- When running source simulation, I thought the Source files were deleted when I accidentally queued up the coupled simulation without switching back to transient mode. However, the source input command actually had a typo: `set saverc` instead of `set savesrc`. I have fixed this in both input files in this repo, as well as the file on the cluster. Hopefully it works this time. Not sure how this typo happened since Im pretty sure I copied it from another file.

- Got a problem with results file not being created because I forgot to comment out the lines involving the results file. (April 26, 2023)

- Got a problem with the detector file bc Serpent did not run its second cycle. Going to make the same changes as for the TREAT model. Not letting the script move on from reading *`com.out`* until the signal is `SIGUSR2`.

- The terminal output had the `Resume Current Iteration` message for over an hour. I commented out the `set ccmaxiter 1` line and hopefully that fixes it. Otherwise, the other changes I just made are garbage basically.

- this change did not work. the simulation got stuck on printing `Resume Current Iteration`. I found another example script from Serpent for coupled transient sims that includes an additional while loop using `iterating` to control the time steps. It looks like I will need to add another loop to the script and tell Serpent to continue with a signal written to *`com.in`*. The simulation did move to the next step when I manually changed the signal.
- I ran into a storage issue, which may have been bc of the huge amounts of terminal output caused by the simulation getting stuck in that loop.

- got an error for the *`.ifc`* file being deleted, which caused the serpent sim to stop. fixed by commenting out the line to delete the file and made the function write to a temp file then copy.



### STAR-CCM+ Model
- will try 1 node like for TREAT sim

- apparently I forgot to put the star file in the directory?!
- got a `error: cannot find symbol` in *`.java`* file for `fw = new FileWriter('ReadTop.txt')` changed to:
```java
    {
    fileTable_2.extract();
    FileWriter readwriter = new FileWriter("ReadTop.txt");
    readwriter.write("Read");
    readwriter.close();
    }
```
- got an error in the *`.java`* file: `error: unreported exception java.io.IOException`. added error handler into code:
```java
if (f.exists())
    try {
    fileTable_2.extract();
    FileWriter readwriter = new FileWriter("ReadTop.txt");
    readwriter.write("Read");
    readwriter.close();
    } catch (IOException e) {
            e.printStackTrace();
    }
```

- got an error: `error: Named object "Body_1" does not exist in manager`. Renamed the region in the cfd file from "Body 1" to "Body_1".

- got an error: 
```
Class: class star.energy.VolumetricHeatSourceProfile
   ConditionManager: star.common.PhysicsValueManager_25795
   error: Condition not found in ConditionManager
```
- updated `Energy Source Option` under `Physics Conditions` in `Region` to `Volumetric Heat Source` so that it hopefully will work with the table exported by **CONSTELATION** now. trying again.

- got an error:
```
VolumetricHeatSourceProfileProfile: profile method properties not set correctly:
Non-existent column "null"
Command: StepSimulation
   error: Server Error
VolumetricHeatSourceProfileProfile: profile method properties not set correctly:
Non-existent column "null"
Command: StepSimulation
   command: CommandComplete
   error: Server Error
```
- fixed the error by adding the following code to the *`.java`* macro. retrying on HPC.
```java
    volumetricHeatSourceProfile_0.getMethod(XyzTabularScalarProfileMethod.class).setData("VolumetricHeat")
```

- got error:
```
Playing macro: /home/warraust/TRIGA/ostr-coupled/load_dataTop.java
load_dataTop.java:64: warning: [deprecation] getValue() in star.common.ScalarPhysicalQuantity has been deprecated
double maxstoppingtime = physicalTimeStoppingCriterion_0.getMaximumTime().getValue();
                                                                         ^
load_dataTop.java:119: error: unreported exception java.io.IOException; must be caught or declared to be thrown
    FileWriter readwriter = new FileWriter("ReadTop.txt");
                            ^
load_dataTop.java:120: error: unreported exception java.io.IOException; must be caught or declared to be thrown
    readwriter.write("Read");
                    ^
load_dataTop.java:121: error: unreported exception java.io.IOException; must be caught or declared to be thrown
    readwriter.close();
```
- after looking at the *`.java`* file, it looks like I did not upload the new file to the HPC after yesterday's edits. However, the HPC file did have the `java.io.IOException` fix and the local file did not. Not sure what is up with that. I am going to make sure both files match and have the fixes for both the error handling and the STAR table stuff.

April 15, 2023:
- not enough STAR licenses on hpc



### Combined
 April 21, 2023:
 - I changed the requested time to 48 hours in hope it will get through the queue before the cluster goes down.

 April 26, 2023:
 - Started sim with 168 hours requested on all jobs and 336 hours on virtual desktop


 ## New Sim with Adiabatic wall

Results from previous successful attempt look really good, but the temperature goes off the scale at one of the measurement positions. To investigate this further, another simulation is to be performed with an adiabatic wall condition instead of a convection wall condition and more things are going to be tracked in STAR over time. No changes are being made to the coupling script or the Serpent model at this time.

In STAR model:
 - added scenes for density and temperature
 - added total energy report, monitor, and plot
 - changed wall condition to be adiabatic

In Serpent model:
- no changes


## Adiabatic Wall and 40 STAR steps per Serpent step

In STAR model:
- change iteration count in *`load_dataTop.java`* file from 100 to 40


In Serpent model:
- change time step from 5e-6 to 2e-6 s
- reduce number of neutrons
    - total neutrons from 5000000000 to 4800000000, with only 2400 cycles instead of 2500
    - utilizes all CPUs and maintains neutrons per cycle with steady source generation
```
%    NAME TYPE Nbins Tmin Tmax
tme tsim 2 2500 0 5E-3
% Total Neutron Population, number of batches, and time structure
set nps  4800000000 2400 tsim
```

In CONSTELATION file:
- change time step to 2E-6
- change STAR STEP input and second STEP input to 40
```
# timestep used for simulation
timestep = 2E-6
# The number of time steps that STAR will simulate before checking for SERPENT completion and then export Data
STAR_STEP = 40
# Second variable used to stay constant in loop
step_length = 40
```

Looks like I cant count zeros. I added too many when changing the number of neutrons. It was 500000000, not 5000000000, so it should be 480000000, not 4800000000. I probably dont even need this many, but we will give it a try.
```
%    NAME TYPE Nbins Tmin Tmax
tme tsim 2 2500 0 5E-3
% Total Neutron Population, number of batches, and time structure
set nps  480000000 2400 tsim
```

Got an error about the He3_Data table from STAR because I forgot to change the time step frequency for updates. Fixed.