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
from functions import *
      
#######################################################
#                  INPUTS                             #
#######################################################
# Serpent input file
Serpent_file = 'TRIGA_D5'

# Time steps need to match up between STAR-CCM+ and Serpent 2 so the information passed between them is happening at the same time. This does not define the time steps for the respective codes.
# timestep used for simulation
timestep = 5E-6
# The number of time steps that STAR will simulate before checking for SERPENT completion and then export Data
STAR_STEP = 100
# Second variable used to stay constant in loop
step_length = 100

# constants and conversions
cm3_to_m3 = 1E-6    # convert cubic centimeters to cubic meters

# cluster commands
run_SERP = "qsub SERPENT_job.sh"
run_STAR1 = "qsub STARTop_Job.sh"

# com file names
comin_name = 'com.in'
comout_name = 'com.out'

# mesh data (NX XMIN XMAX NY YMIN YMAX NZ ZMIN ZMAX)
helium_mesh = '1 -100 100 1 0 100 500 -33.02 32.3675\n'
#fuel_mesh = '1 -500 500 1 -500 500 10 -33.02 30.78\n'

# convert position data from Serpent to STAR, both units and reference frame
reference_conversion = [-11.7653, 2.2225, 67.0111]   # difference in reference frames in cm
unit_conversion = [0, -1/100, -1/100]             # multiplication factor for unit conversion

# STAR csv file for passing heating to STAR from Serpent
Heat_csv_outfile = 'STAR_HeatTop.csv'
Heat_csv_Title = ['X(m)', 'Y(m)', 'Z(m)', 'VolumetricHeat(W/m^3)']
Heat_csv = STAR_csv(Heat_csv_outfile,Heat_csv_Title)

# define the initial Serpent_ifc object (name,header,mesh type, mesh)
Serpent_ifc_top = Serpent_ifc('HE3.ifc','2 helium3 0\n','1\n',helium_mesh)

# define the initial STAR_csv object with file name and header
STARHeat_table = './ExtractedData/He3Data_table.csv'
columns = ['Position[X] (m)', 'Density (kg/m^3)', 'Temperature (K)']
STAR_csv_top = STAR_csv(STARHeat_table,columns)

# detectors
Serpent_det_heat = 'D5Heat'
#Serpent_det_fuel = 'FuelDeposition'

# results file
res_file_name = 'coupled'+Serpent_file+'_res.m'
# keff csv file name
keff_csv_filename = 'coupled'+Serpent_file+'_keff.csv'

# wait time
time_to_wait_default = 3600  # set default time to wait to an hour. most things should not take that long.

# done files
Serpent_done = './SerpentDone.txt'
STARTop_Done = './STARTopDone.txt'
STAR_read = './ReadTop.txt'

# value to print if the com.out file does not contain a readable signal
sig_notdigit = 42


#######################################################
# Create the Serpent input-file for this run          #
# (process id or communication file must be appended) #
#######################################################

# Open original input for reading
file_in = open(Serpent_file, 'r')

# Open a new input file for writing
file_out = open('coupled'+Serpent_file, 'w')

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
file_out.write('ifc '+Serpent_ifc_top.name+'\n\n')
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

# reset wait timers for waiting for the csv file
time_to_wait = 10

# make sure file exists before trying to read it
wait_for_file(STARHeat_table,time_to_wait)

# write the data from the csv file to the ifc file        
csv_to_ifc(STAR_csv_top,Serpent_ifc_top)


##############################################
# Write the initial fuel interface           #
##############################################

# leaving out fuel interface file for now. might add back in later

############################################
# Initialize the fuel temperature solution #
############################################

# removed for now, will write new function and replace as needed

################################
# Start the Serpent simulation #
################################

# Submit SERPENT2 submission script to server
os.system(run_SERP)

# Reset time step
curtime = 0
# Pause Simulation unitl SERPENT2 starts simulating
SERPENTWait = 600000  # wait a week for it to start. the virtual desktop will only last for 2 weeks, so the simulation needs to begin within 1 week to finish. 

# make sure first serpent cycle has been completed. check for com file
wait_for_file(comout_name,SERPENTWait)

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
        fin = open(comout_name, 'r')
        # Read line
        line = fin.readline()
        # Close file
        fin.close()

        # check if signal can be read due to problems of empty files in previous simulations
        line_int = com_check_digit(line,sig_notdigit)

        # Check signal
        if line_int == -1:
            pass
        elif line_int == signal.SIGUSR1.value:
            # Got the signal to resume
            print(signal.SIGUSR1.value)
            print("Resume Current Iteration")
            sleeping = 0
        elif line_int == sig_notdigit:
            # Could not turn the contents of com.out into an integer. Continue and try again.
            print(sig_notdigit)
            print("Resume Current Iteration")
            sleeping = 0
        elif line_int == signal.SIGUSR2.value:
            # Got the signal to move to next time point
            print(signal.SIGUSR2.value)
            print('Move to Next Time Step')
            iterating = 0
            sleeping = 0
        elif line_int == signal.SIGTERM.value:
            # Got the signal to end the calculation
            print(signal.SIGTERM.value)
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
        file_out = open(comout_name, 'w')
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
    detector_file = 'coupled'+Serpent_file+str(curtime) + '.m'
    wait_for_file(detector_file,time_to_wait_default)

    # read in detector file using serpentTools reader
    Serpent_data = serpentTools.read(detector_file)
    # use the serpentTools detector objects for the specified detectors
    DETSerpent_heat = Serpent_data.detectors[Serpent_det_heat]
    #DETSerpent_fuel = Serpent_data.detectors[Serpent_det_fuel]

    ##########################################################
    #### Print Data to CSV in format recognized by STAR-CCM+ #
    ##########################################################
    SerpentHeat_to_Star_csv(DETSerpent_heat,Heat_csv,reference_conversion,unit_conversion)

    ##########################################################
    #### Append Keff data from _res.m file to csv file   #####
    ##########################################################
    wait_for_file(res_file_name,time_to_wait_default)
    keff_res_to_csv(res_file_name,keff_csv_filename,curtime*timestep)

    ##############################################
    # Check on STAR-CCM+ Simulation              #
    ##############################################
    
    if curtime == 0:
        ##############################################
        # Setup the STAR-CCM+ Simulation             #
        ###############################################
        # Simply submits STAR-CCM+ submission script to server
        os.system(run_STAR1)

    # check to see if STAR is done executing
    wait_for_file(STARTop_Done,time_to_wait_default)

    if curtime > 0:
        # Write SERPENTDone.txt file indicating that the current loop has been completed and data extracted
        file_out = open(Serpent_done,'w')
        file_out.write('Done')
        file_out.close

    ###########################
    # Update Top interface    #
    ###########################
    # begin by removing old ifc file to avoid any issues with writing to an exisiting file
    os.remove(Serpent_ifc_top.name)

    # update csv file name
    filename = r'./ExtractedData/He3Data_table_'+str(STAR_STEP)+'.csv'
    STAR_csv_top.name = filename
    
    # make sure file exists before trying to read it
    wait_for_file(filename,time_to_wait_default)
    
    # write from csv to ifc    
    csv_to_ifc(STAR_csv_top,Serpent_ifc_top)
    
    # Update STAR_STEP by number of steps that STAR takes before updating data
    STAR_STEP += step_length

    ###########################
    # Calculate TH-solution for fuel   #
    ###########################

    # removed for now, will write new function and replace as needed

    ###########################
    # Update fuel interface   #
    ###########################

    # removed for now, will write new function and replace as needed

    ##########################################################
    # Tell code to move to next timestep #
    ##########################################################
    file_out = open('com.in','w')
    file_out.write(str(signal.SIGUSR2.value))
    file_out.close()

    ##########################################################
    # Archive Files                                      #####
    ##########################################################
    copyfile(Serpent_ifc_top.name,'Archive/'+Serpent_ifc_top.name+str(curtime))

    #copyfile('fuel.ifc', 'Archive/fuel.ifc' + str(curtime))
    copyfile(Heat_csv.name,'Archive/'+Heat_csv.name+str(curtime)+'.csv')

    if curtime >= 2:
        copyfile('coupled'+Serpent_file+'_res.m','Archive/coupled'+Serpent_file+'_res'+str(curtime)+'.m')

    ##########################################################
    # Delete Files that are not needed between iterations    #
    ##########################################################

    # make sure STAR has read the SerpentDone file before deleting it
    if curtime > 0:
        wait_for_file(STAR_read,time_to_wait)
        os.remove(Serpent_done)
        os.remove(STARTop_Done)
        os.remove(STAR_read)

    # Increment time step
    curtime += 1

    # Copy EOI temperatures to BOI vector

    # removed for now, will write new function and replace as needed


    ####################################
     # Check if simulation has finished #
    ####################################
    if (simulating == 0):
           break
    