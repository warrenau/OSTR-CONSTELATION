#############################################################
#                                                           #
#          STAR and Serpent Coupling Script v 0.6           #
#                   CONSTELATION                            #
#                                                           #
# Based on work created by Cole Leingang    2020/01/10      #
# Modified/ rewritten by: Austin Warren     2023/02/10      #
#############################################################

import os
import signal
import math
import time
import csv
import pandas as pd
import numpy as np
import re
from shutil import copyfile
import serpentTools
#import CONSTELATION_functions as con


# Time steps need to match up between STAR-CCM+ and Serpent 2 so the information passed between them is happening at the same time. This does not define the time steps for the respective codes.
# timestep used for simulation
timestep = 5E-6
# The number of time steps that STAR will simulate before checking for SERPENT completion and then export Data
STAR_STEP = 100
# Second variables used to stay constant in loop
step_length = 100
# convert cubic centimeters to cubic meters
cm3_to_m3 = 1E-6

# mesh data (NX XMIN XMAX NY YMIN YMAX NZ ZMIN ZMAX)
helium_mesh = '1 -100 100 1 0 100 500 -33.02 30.78\n'
fuel_mesh = '1 -500 500 1 -500 500 10 -33.02 30.78\n'

# convert position data from Serpent to STAR, both units and reference frame
reference_conversion = [20.405, 40.605, 226.7903]   # difference in reference frames in cm
unit_conversion = [0, -1/100, -1/100]             # multiplication factor for unit conversion

def position_Serpent_to_STAR(data,reference_conversion,unit_conversion):
    """ Converts position values from Serpent reference frame to STAR reference frame.

    Parameters
    ----------
    data : float,int,array
        data to be converted
    reference_conversion : float,int
        translation from Serpent reference to STAR reference
    unit_conversion : float,int
        unit conversion factor from Serpent reference to STAR reference

    Returns
    -------
    data : float,int,array
        converted data
    """
    data = (data-reference_conversion)*unit_conversion
    return data


# file name and header for STAR csv file
Heat_csv_outfile = r'STAR_HeatTop.csv'
Heat_csv_Title = ['X(m)', 'Y(m)', 'Z(m)', 'VolumetricHeat(W/m^3)']

# function to write out Serpent heating data to STAR csv
def SerpentHeat_to_Star_csv(detector,STAR_csv,reference_conversion,unit_conversion):
    """ Writes Serpent heating detector data out to csv file for STAR to read.

    Parameters
    ----------
    detector : serpentTools Detector object

    outfile : str
        file to open and write to
    title : str or list of str
        header to write on first row of csv file
    """
    outfile = STAR_csv.name
    title = STAR_csv.header
    row = np.zeros(4)
    with open(outfile, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(title)
        for zpoint in range(detector.tallies.shape[0]):
            for ypoint in range(detector.tallies.shape[1]):
                row[0] = position_Serpent_to_STAR(detector.grids['Z'][zpoint,2],reference_conversion[2],unit_conversion[2])
                row[1] = position_Serpent_to_STAR(detector.grids['Y'][ypoint,2],reference_conversion[1],unit_conversion[1])
                row[2] = position_Serpent_to_STAR(detector.grids['X'][0,2],reference_conversion[0],unit_conversion[0])
                row[3] = detector.tallies[zpoint,ypoint]*cm3_to_m3/timestep     # required to match units between the two sims. from J/cm^3 to W/m^3
                csv_writer.writerow(row)

# classes for holding info about ifc and csv files
class Serpent_ifc(object):
    """ interface file object

    Attributes
    ----------
    name : name of ifc file 'he3.ifc'
    header : header of ifc file (TYPE MAT OUT) '2 he3 0\n'
    type : mesh type of ifc file '1\n'
    mesh : mesh of ifc file (NX XMIN XMAX NY YMIN YMAX NZ ZMIN ZMAX)
    data : density and temperature data for ifc file
    """
    def __init__(self,name,header,mesh_type,mesh):
        self.name = name
        self.header = header
        self.mesh_type = mesh_type
        self.mesh = mesh
        self.data = np.array([])

class STAR_csv(object):
    """ STAR-CCM+ csv file object

    Attributes
    ----------
    name : name of csv file r'./ExtractedData/He3Data_table.csv'
    header : header of csv file ['Position', 'Density', 'Temperature']
    data : density and temperature data from csv file
    """
    def __init__(self,name,header):
        self.name = name
        self.header = header
        self.data = np.array([])

# functions for writing data to ifc files
# function to fix any temps below 300K for helium-3 cross sections
def min_temp_fix(array):
    """ Fixes any temperatures below 300K to be 300K for Serpent 2 cross section data

    Parameters
    ----------
    array : numpy array [position, density, temperature]

    Returns
    -------
    array : numpy array [position, density, temperature] with fixed values
    
    """
    for point in range(len(array)):
        if array[point,2] < 300.0:
            array[point,2] = 300.0
    return array

# function to read in csv and convert from pandas to numpy array (should maybe just use numpy array to read in the first place?)
def read_to_numpy(STAR_csv):
    """ Reads in data from STAR-CCM+ csv file, converts the data to a numpy array, and sorts the data by position.

    Parameters
    ----------
    STAR_csv : STAR_csv object

    Returns
    -------
    data : numpy array
    
    """
    file_in = STAR_csv.name
    columns = STAR_csv.header
    data = pd.read_csv(file_in,usecols=columns)
    data = data.to_numpy()
    data = data[data[:,0].argsort()]
    return data

# function to write data from csv file to ifc file
# writes only the density and temperature data, not the position values
# the Serpent interface does not use the position values, since the positions are defined in the Serpent model
def csv_to_ifc(STAR_csv,Serpent_ifc):
    """ Reads in density and temperature data from STAR-CCM+ csv file and writes it to a Serpent 2 ifc file.

    Parameters
    ----------
    STAR_csv : STAR_csv object
        csv file to read from
    Serpent_ifc : Serpent_ifc object
        ifc file to write to
    """
    f = open(Serpent_ifc.name,'w')
    f.write(Serpent_ifc.header)
    f.write(Serpent_ifc.mesh_type)
    f.write(Serpent_ifc.mesh)

    data = read_to_numpy(STAR_csv)
    data = min_temp_fix(data)
    np.savetxt(f, data[:,[1,2]], fmt="%1.6f")

    f.close()


# function to handle waiting for file creation which happens a lot during the execution
def wait_for_file(file,wait):
    time_count = 0
    while not os.path.isfile(file):
        time.sleep(1)
        time_count += 1
        if time_count > wait:
            raise ValueError("%s has not been created or could not be read" % file)

#######################################################
# Create the Serpent input-file for this run          #
# (process id or communication file must be appended) #
#######################################################

# Open original input for reading
file_in = open(r'TRIGA', 'r')

# Open a new input file for writing
file_out = open(r'coupledTRIGA', 'w')

# Write original input to new file

for line in file_in:
    file_out.write(line)

# Close original input file
file_in.close()

# Append Source File Location
file_out.write('\n')
file_out.write('set dynsrc Source 1\n')

# Do not make group constants
file_out.write('\n')
file_out.write('set gcu -1\n')

# Append signalling mode
file_out.write('\n')
file_out.write('set comfile com.in com.out\n')

# Append interface names
file_out.write('\n')
file_out.write('ifc HE3.ifc\n\n')
file_out.write('\n')
#file_out.write('ifc fuel.ifc\n\n')  # not sure that I will use the fuel ifc, but will leave in for now

# Close new input file
file_out.close()


##############################################
# Write the initial He3 interface file for 1st Star Run                      #
# (He3 temperature and density for top two HENRI's will be updated)          #
##############################################
# Write the Mesh Data
STAR_Points = 501

# define the initial Serpent_ifc object
Serpent_ifc_top = Serpent_ifc('HE3.ifc','2 helium3 0\n','1\n',helium_mesh)

# define the initial STAR_csv object with file name and header
filename = r'./ExtractedData/He3Data_table.csv'
columns = ['Position in Cartesian 1[X] (cm)', 'Density(g/cm^3) (kg/m^3)', 'Temperature (K)']
STAR_csv_top = STAR_csv(filename,columns)

# reset wait timers for waiting for the csv file
time_to_wait = 10


# make sure file exists before trying to read it
wait_for_file(filename,time_to_wait)

# write the data from the csv file to the ifc file        
csv_to_ifc(STAR_csv_top,Serpent_ifc_top)


##############################################
# Write the initial fuel interface           #
##############################################

# leaving out fuel interface file for now. might add back in later

############################################
# Initialize the fuel temperature solution #
############################################

TBOI = []
TEOI = []

for i in range(10):
    TBOI.append(300.0)
    TEOI.append(300.0)

################################
# Start the Serpent simulation #
################################

# Submit SERPENT2 submission script to server
run_SERP = "qsub SERPENT_job.sh"
os.system(run_SERP)


# Reset time step
curtime = 0
# Pause Simulation unitl SERPENT2 starts simulating
SERPENTWait = 500000000 

Serpname = r'com.out'
wait_for_file(Serpname,SERPENTWait)

########################
# Loop over time steps #
########################

simulating = 1

while simulating == 1:
    ###################
    # Wait for signal #
    ###################
    sleeping = 1
    while sleeping == 1:
        # Sleep for two seconds
        time.sleep(2)
        # Open file to check if we got a signal
        fin = open('com.out', 'r')
        # Read line
        line = fin.readline()
        # Close file
        fin.close()

        # check if signal can be read due to problems of empty files in previous simulations
        f_digit = line.strip('-\n\r').isdigit()
        sig_notdigit = 42
        if f_digit:
            line_int = int(line)
        elif not f_digit:
            line_int = sig_notdigit
        else:
            print('The com.out file does not exist or cannot be read.')

        # Check signal
        if line_int == -1:
            pass
        elif line_int == signal.SIGUSR1.value:
            # Got the signal to resume
            print(signal.SIGUSR1)
            print("Resume Current Iteration")
            sleeping = 0
        elif line_int == sig_notdigit:
            # Could not turn the contents of com.out into an integer. Continue and try again.
            print(sig_notdigit)
            print("Resume Current Iteration")
            sleeping = 0
        elif line_int == signal.SIGUSR2.value:
            # Got the signal to move to next time point
            print(signal.SIGUSR2)
            print('Move to Next Time Step')
            iterating = 0
            sleeping = 0
        elif line_int == signal.SIGTERM.value:
            # Got the signal to end the calculation
            print(signal.SIGTERM)
            print('END The Simulation')
            iterating = 0
            sleeping = 0
            simulating = 0
        else:
            # Unknown signal
            print("\nUnknown signal read from file, exiting\n")
            print(line)
            # Exit
            quit()
        # Reset the signal in the file
        file_out = open('com.out', 'w')
        file_out.write('-1')
        file_out.close()
    # Check if simulation has finished and break out of iterating
    # loop
    if simulating == 0:
        break
    #########################
    # Import SERPENT2 Data  #
    #########################
    
    # check to make sure the detector file exists
    outputfile = r'coupledTRIGA_det'+str(curtime) + '.m'
    time_counter = 0
    while not os.path.exists(outputfile):
        time.sleep(1)
        time_counter += 1
        if time_counter > SERPENTWait:
            raise ValueError("%s has not been created or could not be read" % Serpname)
            break
    # read in detector file using serpentTools reader
    Serpent_data = serpentTools.read(outputfile)
    # use the serpentTools detector objects for the specified detectors
    DETSerpent2STop = Serpent_data.detectors['Serpent2STop']
    DETFuelDeposition = Serpent_data.detectors['FuelDeposition']

    ##########################################################
    #### Print Data to CSV in format recognized by STAR-CCM+ #
    ##########################################################
    Heat_csv = STAR_csv(Heat_csv_outfile,Heat_csv_Title)
    SerpentHeat_to_Star_csv(DETSerpent2STop,Heat_csv,reference_conversion,unit_conversion)

    ##############################################
    # Check on STAR-CCM+ Simulation              #
    ##############################################
    
    if curtime == 0:
        ##############################################
        # Setup the STAR-CCM+ Simulation             #
        ###############################################
        # Simply submits STAR-CCM+ submission script to server
        run_STAR1 = "qsub STARTop_Job.sh"

        os.system(run_STAR1)

    # check to see if STAR is done executing
    STARTop = r'./STARTopDone.txt'
    time_to_wait = 1000000
    time_counter = 0
    while not os.path.exists(STARTop):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:break

    if curtime > 0:
        # Write SERPENTDone.txt file indicating that the current loop has been completed and data extracted
        file_out = open('./SerpentDone.txt','w')
        file_out.write('Done')
        file_out.close

    ###########################
    # Update Top interface    #
    ###########################
    # begin by removing old ifc file to avoid any issues with writing to an exisiting file
    os.remove('HE3TOP.ifc')
    
    # reset wait timer for csv file
    time_to_wait = 1000000


    # update csv file name
    filename = r'./ExtractedData/He3Data_table_'+str(STAR_STEP)+'.csv'
    STAR_csv_top.name = filename
    
    # make sure file exists before trying to read it
    wait_for_file(filename,time_to_wait)
    
    # write from csv to ifc    
    csv_to_ifc(STAR_csv_top,Serpent_ifc_top)
    
    # Update STAR_STEP by number of steps that STAR takes before updating data
    STAR_STEP += step_length

    ###########################
    # Calculate TH-solution for fuel   #
    ###########################

    # Fuel specific heat capacity
    cp = 998  # J/(kg*K)

    # Calculate EOI temperatures at (nz) axial nodes
    # No heat transfer, just deposition

    for i in range(10):
        # Calculate EOI temperature based on BOI temperature
        # and energy deposition during current time interval

        # Calculate mass of this node (in kg) (z-slice of reactor)
        #   Area of Active Fuel (cm^2)  * Length of Node (cm) * density (g/cm^3)  * conversion (g to kg)
        #   314 Fuel Assemblies (93.16 cm^2 each)
        #   20 Control Rod Assemblies ( Fuel Assembly Area - Control Rod Area) (65.65 cm^2 each)
        #   4 HENRI Assemblies (Fuel Assembly Area - HENRI Area) (73.53 cm^2)
        #   Density of Fuel assumed to be 1.72 g/cm^3 (mostly Graphite)
        #   z-slice (10 slices / total length of reactor (121 cm))
        m = ((93.16*314)+(65.65*20)+(75.53*4)) * 12.1 * 1.72 * 1e-3

        # Calculate initial heat in this axial node
        Q = TBOI[i] * (cp * m)

        # The interface output is Joules in case of time dependent
        # simulation, no need to multiply with time step
        dQ = data_fuelpass[i]

        # Calculate new temperature based on new amount of heat
        TEOI[i] = (Q + dQ) / (cp * m)

    ###########################
    # Update interface        #
    ###########################

    file_out = open('./fuel.ifc', 'w')

    # Write the header line (TYPE MAT OUT)
    file_out.write('2 fuel 0\n')

    # Write the mesh type
    file_out.write('1\n')

    # Write the mesh size (NX XMIN XMAX NY YMIN YMAX NZ ZMIN ZMAX)
    file_out.write(fuel_mesh)

    # Write updated fuel temperatures
    for i in range(10):
        # Use the base density throughout the simulation
        # Write density and temperature at this layer
        file_out.write('-1.72 {}\n'.format(TEOI[i]))

    file_out.close()

    ##########################################################
    # Tell code to move to next timestep #
    ##########################################################
    file_out = open('com.in','w')
    file_out.write(str(signal.SIGUSR2.value))
    file_out.close()

    ##########################################################
    # Archive Files                                      #####
    ##########################################################
    copyfile('HE3TOP.ifc','Archive/HE3TOP.ifc'+str(curtime))

    copyfile('fuel.ifc', 'Archive/fuel.ifc' + str(curtime))
    copyfile('STAR_HeatTop.csv','Archive/Star_HeatTop'+str(curtime)+'.csv')

    if curtime >= 2:
        copyfile('coupledTreat_res.m','Archive/coupledTreat_res'+str(curtime)+'.m')
    # Delete Files that are not needed between iterations
    time.sleep(60)
    os.remove(STARTop)

    if curtime > 0:
        os.remove('SerpentDone.txt')
    # Increment time step
    curtime += 1

    # Copy EOI temperatures to BOI vector

    for i in range(10):
        TBOI[i] = TEOI[i]
    ####################################
     # Check if simulation has finished #
    ####################################
    if (simulating == 0):
           break

    time.sleep(30)
    file_out = open('com.in','w')
    file_out.write(str(signal.SIGUSR2))
    file_out.close()