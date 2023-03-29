



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
