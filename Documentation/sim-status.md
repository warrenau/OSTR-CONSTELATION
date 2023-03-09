



---
## Prepping OSTR Serpent Model
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