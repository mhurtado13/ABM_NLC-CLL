
import numpy as np
import pandas as pd
import pcdl

def collect_data(dir_output, config_file):

    mcdsts = pcdl.TimeSeries(dir_output, settingxml=config_file, verbose = False, microenv=False, graph=False) 
    timesteps = mcdsts.get_mcds_list()

    positions = []
    for days in range(0,14):
        hours = 24*days
        positions.append(hours)

    #Extract day 0
    initial = timesteps[0].get_cell_df(states=1)

    ######## Calculate CLL viability and concentration
    alive_initial = len(initial[(initial['cell_type']=="cancer")])
    apoptotic_initial = len(initial[(initial['cell_type']=="apoptotic")])
    dead_initial = len(initial[(initial['cell_type']=="dead")])
    CLL_initial = alive_initial + apoptotic_initial + dead_initial
    
    alive = [alive_initial]
    dead = [dead_initial]
    apoptotic = [apoptotic_initial]

    for i in range(1, len(positions)):
        step = timesteps[positions[i]].get_cell_df(states=1)
        number_alive = len(step[(step['cell_type']=='cancer')&(step['dead']==False)]) #step['dead'] is only a formality cause all cells are considered 'alive', 'dead' is another celltype for this model
        number_apoptotic = len(step[(step['cell_type']=='apoptotic')&(step['dead']==False)])
        number_dead = len(step[(step['cell_type']=='dead')&(step['dead']==False)])
        alive.append(number_alive)
        dead.append(number_dead)
        apoptotic.append(number_apoptotic)

    CLL_alive = pd.Series(alive, name="Cells_alive")
    CLL_apoptotic = pd.Series(apoptotic, name = "Cells_apoptotic")
    CLL_dead = pd.Series(dead, name = "Cells_dead")

    #viability at time t =  CLL alive at time t / (CLL alive + CLL apoptotic + CLL dead) at time t
    viability = []
    for i in range(len(CLL_alive)):
        number = (CLL_alive[i] / (CLL_alive[i] + CLL_apoptotic[i] + CLL_dead[i])) * 100
        viability.append(number)

    viability = pd.Series(viability, name = "CLL viability")

    #concentration at time t =  CLL alive at time t / (CLL initial)
    concentration = []
    for i in range(len(CLL_alive)):
        number = ((CLL_alive[i] + CLL_apoptotic[i] + CLL_dead[i])/CLL_initial)*100
        concentration.append(number)

    concentration = pd.Series(concentration, name = "CLL concentration")

    ######## Calculate monocytes, macrophages, NLC appearance
    monocytes_initial = len(initial[(initial['cell_type']=="monocytes")])
    macrophages_initial = len(initial[(initial['cell_type']=="macrophages")])
    nlc_initial = len(initial[(initial['cell_type']=="NLCs")])

    monocytes = [monocytes_initial]
    macrophages = [macrophages_initial]
    nlc = [nlc_initial]

    for i in range(1, len(positions)):
        step = timesteps[positions[i]].get_cell_df(states=1)
        number_monocytes = len(step[(step['cell_type']=='monocytes')]) #step['dead'] is only a formality cause all cells are considered 'alive', 'dead' is another celltype for this model
        number_macrophages = len(step[(step['cell_type']=='macrophages')])
        number_nlc = len(step[(step['cell_type']=='NLCs')])
        monocytes.append(number_monocytes)
        macrophages.append(number_macrophages)
        nlc.append(number_nlc)

    Monocytes = pd.Series(monocytes, name="Monocytes")
    Macrophages = pd.Series(macrophages, name = "Macrophages")
    NLCs = pd.Series(nlc, name = "NLCs")

    return viability, concentration, Monocytes, Macrophages, NLCs