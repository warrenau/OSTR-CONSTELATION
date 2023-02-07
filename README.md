# OSTR-CONSTELATION
Coupled model using STAR-CCM+ and Serpent 2 for a HENRI-based experiment in the Oregon State TRIGA Reactor. Based on **CONSTELATION** for HENRI in TREAT ([CONSTELATION GitHub](https://github.com/warrenau/CONSTELATION)).

This project utilizes the same software, structure, and coupling method as **CONSTELATION** for TREAT, but applies it to the OSTR with a custom designed experiment. The purpose is to quantify the extent to which the coupled model **CONSTELATION** is accurate in predicting the density evolution of the helium-3 during an injection for a TREAT transient pulse and its effects on the reactor. The OSTR and the experiment designed for it will provide the data for this quantification. This project contains the code, scripts, and instructions to execute the coupled STAR-CCM+ and Serpent 2 simulation for the OSTR.

## Requirements

- Python 3 (tested using Python 3.9 from the Anaconda distribution)
- STAR-CCM+ (used version 2020.2.1 on INL HPC)
- Serpent 2 (used version 2.1.31 on INL HPC)
