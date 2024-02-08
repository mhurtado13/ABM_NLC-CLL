from SALib.sample import latin, sobol
import pandas as pd
import numpy as np
import sys

# Number of Samples
nsamples = int(sys.argv[1]) 

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

#Generate sobol samples
sobol_samples = sobol.sample(problem, nsamples)

param_names = list(param_ranges.keys())
sobol_samples = pd.DataFrame(sobol_samples, columns=param_names)

#Save output
sobol_samples.to_csv('../data_output/sobol_samples.csv', index=False)
