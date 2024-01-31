from SALib.sample import latin, sobol
import pandas as pd
import numpy as np

# Number of Samples
nsamples = 100 

# Number of parameters
nparams = 8 

#Ranges for each parameter
param_ranges = {
    'cell_ecm_repulsion': [0, 75],
    'contact_cell_ECM_threshold': [0, 2],
    'contact_cell_cell_threshold': [0, 3.5],
    'cell_junctions_attach_threshold': [0, 1],
    'cell_junctions_detach_threshold': [0, 1],
    'migration_bias': [0, 1],
    'migration_speed': [0, 1],
    'persistence': [0, 100]
}

#Define the problem for SALib
problem = {
    'num_vars': nparams,
    'names': list(param_ranges.keys()),
    'bounds': [[0, 75], [0, 2], [0, 3.5], [0, 1], [0, 1], [0, 1], [0, 1], [0, 100]] 
}

#Generate Latin hypercube samples
lhs_samples = latin.sample(problem, nsamples)
#Generate sobol samples
sobol_samples = sobol.sample(problem, nsamples)

param_names = list(param_ranges.keys())
lhs_samples = pd.DataFrame(lhs_samples, columns=param_names)
sobol_samples = pd.DataFrame(sobol_samples, columns=param_names)

#Save output
lhs_samples.to_csv('lhs_samples.csv', index=False)
sobol_samples.to_csv('sobol_samples.csv', index=False)