import xml.etree.ElementTree as ET
import subprocess
import pandas as pd
import sys
import numpy as np

input_file_path = sys.argv[1]

#Load samples from LHS or Sobol
samples_lhs = np.loadtxt('data_output/lhs_samples.csv', delimiter=",", skiprows=1)
#sobol_samples = pd.read_csv('../data_output/sobol_samples.csv')

#Load xml file
tree = ET.parse(input_file_path)
root = tree.getroot()

#param_names = {"cell_cell_repulsion_strength": 0, "cell_cell_adhesion_strength": 1, "relative_maximum_adhesion_distance": 2, 
#               "cell_BM_adhesion_strength": 3, "speed": 4, "migration_bias": 5, "secretion_rate": 6, "fluid_change_rate":7}

param_names = {"cell_cell_repulsion_strength": 0, "cell_cell_adhesion_strength": 1}

replicates = 2 #For bootstrapping
# Loop over each iteration in the LHS data
for i, lhs_iteration in enumerate(samples_lhs): #Taking rows where i = row number and lhs_iteration = list of parameters from corresponding row
# Loop over each parameter and update its value in the XML file
    for param_name, lhs_col_index in param_names.items(): # param_name = parameter name and lhs_col_index = column number
        param_value = lhs_iteration[lhs_col_index] #Extract each value [i, lhs_col_index]
        param_element = root.find(f".//{param_name}") #Find the param name in XML file
        param_element.text = str(param_value) #Update the text of xml file with extracted value 

    # Write the updated XML to a string
    updated_xml_str = ET.tostring(root, encoding="unicode", method="xml")

    # Define the command to call your C++ software with the updated XML as input
    command = ["./project", "./config/NLC_CLL.xml"]
    stdin_str = updated_xml_str

    for i in range(replicates): #replicates is for bootstrapping, we run the simulation with updated value # (replicates) times
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

    if i == samples_lhs.shape[0]:
        print("Analysis done :)")
    else:
        print("Next set") #Continue to next row 