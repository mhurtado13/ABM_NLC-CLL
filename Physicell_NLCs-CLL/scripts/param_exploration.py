import xml.etree.ElementTree as ET
import subprocess
import pandas as pd
import sys
import numpy as np
import os
import random
from multiprocessing import Pool
from pymoo.core.problem import Problem
from multiprocessing.pool import ThreadPool

def model_simulation(input_file_path, replicates, *args):                
    
    tree = ET.parse(input_file_path) #Load xml file
    root = tree.getroot()

    param_behaviors = {'cancer':{'uptake_rate': 0, 'speed': 1, 'transformation_rate': 2},
                    'monocytes':{'speed': 3, 'dead_phagocytosis_rate': 4},
                    'macrophages':{'speed': 5, 'dead_phagocytosis_rate': 6},
                    'NLCs': {'secretion_rate': 7, 'speed': 8, 'dead_phagocytosis_rate': 9}}
    
    for i, celltype in enumerate(param_behaviors.keys()): #i = number of keys name and celltype = cell type
        for param, column in param_behaviors[celltype].items(): #param = parameter name and column = column number
            if celltype == 'cancer' and param == 'uptake_rate':
                param_value = args[column] #Extract each value [i, col_index]
                param_element = root.find(f".//*[@name='{celltype}']//*[@name='anti-apoptotic factor']//{param}") #Find the param name in XML file
                param_element.text = str(param_value)
            elif celltype == 'cancer' and param == 'transformation_rate':
                param_value = args[column] #Extract each value [i, col_index]
                param_element = root.find(f".//*[@name='{celltype}']//{param}/[@name='apoptotic']") #Find the param name in XML file
                param_element.text = str(param_value)
            elif celltype == 'NLCs' and param == 'secretion_rate':
                param_value = args[column] #Extract each value [i, col_index]
                param_element = root.find(f".//*[@name='{celltype}']//*[@name='anti-apoptotic factor']//{param}") #Find the param name in XML file
                param_element.text = str(param_value)
            else:
                param_value = args[column] #Extract each value [i, col_index]
                param_element = root.find(f".//*[@name='{celltype}']//{param}") #Find the param name in XML file
                param_element.text = str(param_value)

    # Define the command to call your C++ software with the updated XML as input
    command = ["./project", "./config/NLC_CLL.xml"]
            
    for i in range(replicates): #replicates is for bootstrapping, we run the simulation with updated value # (replicates) times
        # Random seed for each simulation
        param_element = root.find(".//random_seed") #Find the random seed in XML file
        param_element.text = str(random.randint(0,4294967295))

        # Write the updated XML to a string
        updated_xml_str = ET.tostring(root, encoding="unicode", method="xml")
        stdin_str = updated_xml_str

        # Call the C++ software using subprocess
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(stdin_str.encode())

        # Check that the Physicell ran successfully
        if proc.returncode != 0:
            print("Error running Physicell")
            print(stderr.decode())
            continue

        subprocess.run(["python", "scripts/collect_data.py"]) #We collect the data at each iteration

    subprocess.run(["python", "scripts/merge_data.py"]) #Merge data of replicates 

pool = ThreadPool(int(sys.argv[1])) 
n_replicates = int(sys.argv[2])

default_values = [1.0, 1.0, 5e-5, 1.0, 25e-2, 1.0, 92e-2, 1.0, 1.0, 4e-2]

input = {'uptake_rate_cancer': 1.0, 'speed_cancer': 1.0, 'transformation_rate_cancer': 5e-5,
                  'speed_monocytes':1.0, 'dead_phagocytosis_rate_monocytes':25e-2, 'speed_macrophages':1.0,
                  'dead_phagocytosis_rate_macrophages':92e-2, 'secretion_rate_NLCs':1.0, 'speed_NLCs':1.0,
                  'dead_phagocytosis_rate_NLCs':4e-2}

#death rate apoptotic cells
#number of initial apoptotic cells 
#number of initial CLL cells

vals = [10, 40, 60, 80, 100, 130]

def reset_values(data, values_def):        
    for i, key in enumerate(data.keys()):
        data[key] = values_def[i]

for parameter in input.keys():
    x = []
    for i in vals:
        input[parameter] = i
        x.append(tuple(input.values()))
        reset_values(input, default_values)

    params = [(("./config/NLC_CLL.xml", n_replicates) + x[contador]) for contador in range(len(vals))]

    pool.starmap(model_simulation, params)

pool.close()