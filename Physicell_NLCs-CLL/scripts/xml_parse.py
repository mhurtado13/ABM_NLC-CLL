import xml.etree.ElementTree as ET
import subprocess
import pandas as pd
import sys
import numpy as np
import os
import random
from multiprocessing import Pool
 
input_file_path = sys.argv[1]
nodes = int(sys.argv[2])
replicates = int(sys.argv[3]) #For bootstrapping

#Load samples from LHS or Sobol
#samples_sobol_all = np.loadtxt('data_output/sobol_samples.csv', delimiter=",", skiprows=1)

# Folder containing the CSV files
folder = "data_output/subspaces"

# Initialize an empty list to store child files
dataframes_list = []

# Iterate over files in the folder
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    
    # Check if it's a file (not a directory) 
    if os.path.isfile(file_path):
        # Read the CSV file 
        dataframe = np.loadtxt(file_path, delimiter=",", skiprows=1)
        dataframes_list.append(dataframe)
        
def parsing(samples_sobol):    
    #Load xml file
    tree = ET.parse(input_file_path)
    root = tree.getroot()

    param_behaviors = {'cancer':{'uptake_rate': 0, 'speed': 1, 'transformation_rate': 2},
                    'monocytes':{'speed': 3, 'dead_phagocytosis_rate': 4},
                    'macrophages':{'speed': 5, 'dead_phagocytosis_rate': 6},
                    'NLCs': {'secretion_rate': 7, 'speed': 8, 'dead_phagocytosis_rate': 9}}

    #param_names = {"cell_cell_repulsion_strength": 0, "cell_cell_adhesion_strength": 1}

    # Loop over each iteration in the LHS data
    for i, sobol_iteration in enumerate(samples_sobol): #Taking rows where i = row number and lhs_iteration = list of parameters from corresponding row
        for celltype, celltype_param in param_behaviors.items(): #param_name = parameter name and lhs_col_index = column number
            for param, column in celltype_param.items():
                if(celltype == 'cancer' and param == 'uptake_rate'):
                    param_value = sobol_iteration[column] #Extract each value [i, lhs_col_index]
                    param_element = root.find(f".//*[@name='{celltype}']//*[@name='anti-apoptotic factor']//{param}") #Find the param name in XML file
                    param_element.text = str(param_value)
                elif(celltype == 'cancer' and param == 'transformation_rate'):
                    param_value = sobol_iteration[column] #Extract each value [i, lhs_col_index]
                    param_element = root.find(f".//*[@name='{celltype}']//{param}/[@name='apoptotic']") #Find the param name in XML file
                    param_element.text = str(param_value)
                elif(celltype == 'NLCs' and param == 'secretion_rate'):
                    param_value = sobol_iteration[column] #Extract each value [i, lhs_col_index]
                    param_element = root.find(f".//*[@name='{celltype}']//*[@name='anti-apoptotic factor']//{param}") #Find the param name in XML file
                    param_element.text = str(param_value)
                else:
                    param_value = sobol_iteration[column] #Extract each value [i, lhs_col_index]
                    param_element = root.find(f".//*[@name='{celltype}']//{param}") #Find the param name in XML file
                    param_element.text = str(param_value)

        # Define the command to call your C++ software with the updated XML as input
        command = ["./project", "./config/NLC_CLL.xml"]
        
        for i in range(replicates): #replicates is for bootstrapping, we run the simulation with updated value # (replicates) times
            # Random seed for each simulation
            param_element = root.findall(".//random_seed") #Find the random seed in XML file
            param_element.text = random.randint(0,4294967295)

            # Write the updated XML to a string
            updated_xml_str = ET.tostring(root, encoding="unicode", method="xml")
            stdin_str = updated_xml_str

            # Call the C++ software using subprocess
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(stdin_str.encode())

            # Check that the Physicell ran successfully
            if proc.returncode != 0:
                print(f"Error running Physicell for iteration {i}")
                print(stderr.decode())
                continue

            subprocess.run(["python", "scripts/collect_data.py"]) #We collect the data at each iteration

        subprocess.run(["python", "scripts/merge_data.py"]) #Merge data of replicates 
        print("Next set") #Continue to next row 

def pool_handler():
    p = Pool(nodes)
    p.map(parsing, dataframes_list)

if __name__ == '__main__':
    pool_handler()
