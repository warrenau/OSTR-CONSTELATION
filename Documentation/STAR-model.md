# STAR-CCM+ Model

This document details the STAR-CCM+ portion of **CONSTELATION**. Obtaining, verifying, and validating the model is up to the user. 

Development of OSTR HENRI STAR-CCM+ model can be found here: [OSTR STAR Model](https://github.com/warrenau/ostr-henri-starccm).



# Java Macro
The *`.java`* macro used to run the STAR-CCM+ simulation is created by STAR-CCM+, but needs to be modified. One of the modifications is to provide **CONSTELATION** with confirmation that the STAR-CCM+ simulation has read the *`SerpentDone.txt`* file so that the file is not deleted before the STAR-CCM+ simulation has time to read it. The following code checks if the done file exists, and if it does, a new file is created and written to for **CONSTELATION** to read.
```java
if (f.exists())
    {
    fileTable_2.extract();
    fw = new FileWriter("./ReadTop.txt",true)
    fw.write("Read")
    fw.close
    }
```