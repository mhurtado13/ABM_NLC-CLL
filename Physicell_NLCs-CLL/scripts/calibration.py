import xml.etree.ElementTree as ET
import subprocess
import pandas as pd
import sys
import numpy as np
import os
import random
from multiprocessing import Pool

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

    viability = np.loadtxt('data_output/viability.csv', delimiter=",", skiprows=1)
    concentration = np.loadtxt('data_output/concentration.csv', delimiter=",", skiprows=1)

    ##Remove .csv files to free space
    os.remove('data_output/viability.csv')
    os.remove('data_output/concentration.csv')

    return viability, concentration


from pymoo.core.problem import Problem
from multiprocessing.pool import ThreadPool

experimental = np.loadtxt('../Netlogo_NLCs-CLL/filtered_fused_9patients.csv', delimiter=",", skiprows=1)
viability_exp = experimental[:,1]
concentration_exp = experimental[:,2]
pop_size = int(sys.argv[1])
pool = ThreadPool(int(sys.argv[2])) # Adjust the number of threads as needed (how many tasks can run concurrently.)
n_replicates = int(sys.argv[3])
n_gen = int(sys.argv[4])

class calibrationProb(Problem):
    def __init__(self):
        super().__init__(n_var = 10,
                       n_obj = 2,
                       xl = np.array([0.9, 0.9, 4e-5, 0.9, 24e-2, 0.9, 91e-2, 0.9, 0.9, 3e-2]),
                       xu = np.array([1.2, 1.2, 6e-5, 1.2, 26e-2, 1.2, 93e-2, 1.2, 1.2, 5e-2]))
        
    def _evaluate(self, x, out):

        # Prepare the parameters for the pool
        params = [(("./config/NLC_CLL.xml", n_replicates) + tuple(x[i])) for i in range(pop_size)]

        # Calculate the function values in a parallelized manner and wait until done
        results = pool.starmap(model_simulation, params)

        #Objective functions
        obj1 = []
        obj2 = []
        for i in range(pop_size):
            viability, concentration = results[i]
            #RMSE of viability
            rmse_viability = np.sqrt(np.sum((viability - viability_exp)**2) / 10) #10 is the total of time points
            obj1.append(rmse_viability)
            #RMSE of concentration
            rmse_concentration = np.sqrt(np.sum((concentration - concentration_exp)**2) / 10) #10 is the total of time points
            obj2.append(rmse_concentration)

        #Stacking objectives to "F" 
        out["F"] = np.column_stack([obj1, obj2])

        pool.close()


NLC_problem = calibrationProb()

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination

algorithm_nsga = NSGA2(pop_size=pop_size)

termination = get_termination("n_gen", n_gen)

res = minimize(NLC_problem,
               algorithm_nsga,
               termination,
               seed=1,
               verbose=True)

 
print(res.X)
print(res.F)

np.savetxt('data_output/Space_values.csv', res.X, delimiter=",")
np.savetxt('data_output/Objective_values.csv', res.F, delimiter=",")