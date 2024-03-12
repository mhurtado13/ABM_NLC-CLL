import xml.etree.ElementTree as ET
import subprocess
import pandas as pd
import sys
import numpy as np
import os
import random
from multiprocessing import Pool

def model_simulation(input_file_path, replicates, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10):                
    #Load xml file
    tree = ET.parse(input_file_path)
    root = tree.getroot()
    #Inputs
    inputs = [param1, param2, param3, param4, param5, param6, param7, param8, param9, param10]
    param_behaviors = {'cancer':{'uptake_rate': 0, 'speed': 1, 'transformation_rate': 2},
                    'monocytes':{'speed': 3, 'dead_phagocytosis_rate': 4},
                    'macrophages':{'speed': 5, 'dead_phagocytosis_rate': 6},
                    'NLCs': {'secretion_rate': 7, 'speed': 8, 'dead_phagocytosis_rate': 9}}
    
    for celltype, celltype_param in param_behaviors.items(): #param_name = parameter name and lhs_col_index = column number
        for param, column in celltype_param.items():
            if(celltype == 'cancer' and param == 'uptake_rate'):
                param_value = inputs[column] #Extract each value [i, lhs_col_index]
                param_element = root.find(f".//*[@name='{celltype}']//*[@name='anti-apoptotic factor']//{param}") #Find the param name in XML file
                param_element.text = str(param_value)
            elif(celltype == 'cancer' and param == 'transformation_rate'):
                param_value = inputs[column] #Extract each value [i, lhs_col_index]
                param_element = root.find(f".//*[@name='{celltype}']//{param}/[@name='apoptotic']") #Find the param name in XML file
                param_element.text = str(param_value)
            elif(celltype == 'NLCs' and param == 'secretion_rate'):
                param_value = inputs[column] #Extract each value [i, lhs_col_index]
                param_element = root.find(f".//*[@name='{celltype}']//*[@name='anti-apoptotic factor']//{param}") #Find the param name in XML file
                param_element.text = str(param_value)
            else:
                param_value = inputs[column] #Extract each value [i, lhs_col_index]
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

    viability = np.loadtxt('data_output/viability.csv', delimiter=",", skiprows=1)
    concentration = np.loadtxt('data_output/concentration.csv', delimiter=",", skiprows=1)

    return viability, concentration


from pymoo.core.problem import Problem
import math

experimental = np.loadtxt('../Netlogo_NLCs-CLL/filtered_fused_9patients.csv', delimiter=",", skiprows=1)
viability_exp = experimental[:,1]
concentration_exp = experimental[:,2]
N = 13

class calibrationProb(Problem):
    def __init__(self):
        super().__init__(n_var = 10,
                       n_obj = 2,
                       xl = np.array([0.9, 0.9, 4e-5, 0.9, 24e-2, 0.9, 91e-2, 0.9, 0.9, 3e-2]),
                       xu = np.array([1.2, 1.2, 6e-5, 1.2, 26e-2, 1.2, 93e-2, 1.2, 1.2, 5e-2]))
        
    def _evaluate(self, x, out):
        viability, concentration = model_simulation("./config/NLC_CLL.xml", 1, x[:,0], x[:,1], x[:,2], x[:,3], x[:,4], x[:,5], x[:,6], x[:,7], x[:,8], x[:,9])

        #Objective functions
        obj1 = np.sqrt(np.sum((viability - viability_exp)**2) / N) #RMSE of viability
        obj2 = np.sqrt(np.sum((concentration - concentration_exp)**2) / N) #RMSE of concentration

        #Stacking objectives to "F" 
        out["F"] = np.column_stack([obj1, obj2])


NLC_problem = calibrationProb()

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

algorithm_nsga = NSGA2(pop_size=500)

from pymoo.termination import get_termination
termination = get_termination("n_gen", 1000)

res = minimize(NLC_problem,
               algorithm_nsga,
               termination,
               seed=1,
               verbose=True)

print(res.X)
print(res.F)