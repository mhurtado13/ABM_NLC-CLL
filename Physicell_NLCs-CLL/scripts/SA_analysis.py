from SALib.analyze import sobol ##sobol is a type of SA analysis implemented in SALib
from SALib.sample import saltelli
from SALib.sample import latin
import pandas as pd
import numpy as np
from SALib.analyze import rbd_fast

# Number of parameters
nparams = 2 

#Ranges for each parameter
#param_ranges = {
#    'cell_cell_repulsion_strength': [0, 75],
#    'cell_cell_adhesion_strength': [0, 2],
#    'relative_maximum_adhesion_distance': [0, 3.5],
#    'cell_BM_adhesion_strength': [0, 1],
#    'speed': [0, 1],
#    'migration_bias': [0, 1],
#    'secretion_rate': [0, 1],
#    'fluid_change_rate': [0, 100]
#}

param_ranges = {
    'cell_cell_repulsion_strength': [1, 10],
    'cell_cell_adhesion_strength': [0, 0.6]
}

#Define the problem for SALib
problem = {
    'num_vars': nparams,
    'names': list(param_ranges.keys()),
    'bounds': [[1, 10], [0, 0.6]] 
}

#Sampling
samples_lhs = np.loadtxt('../data_output/lhs_samples.csv', delimiter=",", skiprows=1)
#param_values =  latin.sample(problem, 3)
#param_values = saltelli.sample(problem, 2, calc_second_order=False)

#Read output of simulation
output = pd.read_csv('../data_output/viability.csv', index_col=0).to_numpy()

# Calculate the correlation matrix
corr_matrix = np.corrcoef(output.to_numpy().T)

# Perform analysis: Compute sensitivity indices
output = output.iloc[0:8,1].values

Si = sobol.analyze(problem, output, print_to_console=True) 
# Print the first-order and total sensitivity indices for each parameter
print('Sobol Analysis Results:')
for i, param in enumerate(problem['names']):
   print(f"{param}: S1={Si['S1'][i]:.3f}, ST={Si['ST'][i]:.3f}")

#https://stackoverflow.com/questions/55634208/does-salib-sensitivity-analysis-package-support-only-one-column-vector-input
#https://notebook.community/locie/locie_notebook/misc/Sensitivity_analysis   
