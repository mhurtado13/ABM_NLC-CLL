import anndata as ad  
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import pcdl
import os

dir_output = 'output'
mcdsts = pcdl.TimeSeries(dir_output, settingxml='config/NLC_CLL.xml') 
timesteps = mcdsts.get_mcds_list()

#Extract positions corresponding to days 1-13
positions = []
for days in range(0,14):
    hours = 24*days
    positions.append(hours)

#Initial CLL cells
initial = timesteps[0].get_cell_df(states=2)
CLL_initial = len(initial[(initial['cell_type']=="cancer_cells")|(initial['cell_type']=="apoptotic")])

#Calculate alive and dead cells across days
alive = [CLL_initial]
dead = [0]
for i in range(1, len(positions)):
  step = timesteps[positions[i]].get_cell_df(states=2)
  number_alive = len(step[((step['cell_type']=='cancer_cells')|(step['cell_type']=='apoptotic'))&(step['dead']==False)])
  number_dead = len(step[step['dead']==True])
  alive.append(number_alive)
  dead.append(number_dead)

CLL_alive = pd.Series(alive, name="Cells_alive")
CLL_dead = pd.Series(dead, name = "Cells_dead")

#Calculate viability =  CLL alive / (CLL alive + CLL dead)
viability = []
for i in range(len(CLL_alive)):
    number = (CLL_alive[i]/(CLL_alive[i]+CLL_dead[i]))*100
    viability.append(number)

####Remove day 4, 5, 11, 12 because of experimental
viability = np.delete(viability, [4,5,11,12], axis=0)

viability = pd.Series(viability, name = "CLL viability")

#Cells alive / Volume
volumen = 0.0000648 #cm3 648x10**-7

concentration = []
for i in CLL_alive:
    number = round(i/volumen,2)*100
    concentration.append(number)

####Remove day 4, 5, 11, 12 because of experimental
concentration = np.delete(concentration, [4,5,11,12], axis=0)

concentration = pd.Series(concentration, name = "CLL concentration")

df = pd.concat([viability, concentration], axis=1)

file_csv = 'data_output/data.csv'

#If the file already exists
if os.path.exists(file_csv):
    old_data = pd.read_csv(file_csv)
    new_data = pd.concat([old_data, df], axis=1)
    new_data.to_csv(file_csv, index=False, header=True)
else:
    df.to_csv(file_csv, index=False, header=True)