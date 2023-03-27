# STAR-CCM+ Model

This document details the STAR-CCM+ portion of **CONSTELATION**. Obtaining, verifying, and validating the model is up to the user. 

Development of OSTR HENRI STAR-CCM+ model can be found here: [OSTR STAR Model](https://github.com/warrenau/ostr-henri-starccm).



# Java Macro
The *`.java`* macro used to run the STAR-CCM+ simulation is created by STAR-CCM+, but needs to be modified. One of the modifications is to provide **CONSTELATION** with confirmation that the STAR-CCM+ simulation has read the *`SerpentDone.txt`* file so that the file is not deleted before the STAR-CCM+ simulation has time to read it. The following code checks if the done file exists, and if it does, a new file is created and written to for **CONSTELATION** to read.
```java
if (f.exists())
    {
    fileTable_2.extract();
    fw = new FileWriter("./ReadTop.txt",true);
    fw.write("Read");
    fw.close();
    }
```

To modify the *`.java`* macro for using different models, there are a couple of things that need to be changed. The first is the name of the `Region` that the macro will look at. I originally thought this was the Body `Part` because they have the same name and I found the `Part` first, but it threw an error when the `Region` was not named correctly.
```java
Region region_0 = 
    simulation_0.getRegionManager().getRegion("Body_1");
```
The part in quotes is the name listed in the STAR-CCM+ simulation. The image below shows the corresponding STAR-CCM+ dropdown for the example of code above.

![STAR-CCM+ Model Geometry Dropdown](pics/ostr-coupled-region-dropdown.PNG)

Additionally, the number of time steps to be simulated between stops must be altered for each simulation. The time step value for the STAR-CCM+ simulation will most likely be smaller than the time step for the Serpent 2 simulation, possibly by multiple orders of magnitude. The input in the *`.java`* macro is the number of time steps STAR-CCM+ will simulate before waiting for the Serpent 2 time step to finish. For example, if the time step for the Serpent 2 simulation is 5E-6 s and the time step for the STAR-CCM+ simulation is 5E-8 s, the value input in the macro should be 100. Below is an example of the code where this value needs to be changed.

```java
    simulation_0.getSimulationIterator().setNumberOfSteps(100);
```
```java
    simulation_0.getSimulationIterator().step(100);
```

Both of these lines should have a matching number to each other that is the correct ratio of Serpent 2 time step to STAR-CCM+ time step.