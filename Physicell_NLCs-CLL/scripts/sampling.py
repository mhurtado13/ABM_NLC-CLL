from SALib.sample import latin, sobol
import pandas as pd
import numpy as np
import sys

# Number of Samples
nsamples = int(sys.argv[1]) 

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

default_values = {'cell_cell_repulsion_strength': 0.15, 'cell_cell_adhesion_strength': 1.0}

#Define the problem for SALib
problem = {
    'num_vars': len(default_values),
    'names': default_values.keys(),
    'bounds': np.array([[0,0],[0.3,2.0]]).T # 100% percent of variation from default values 
}

#Generate sobol samples
sobol_samples = sobol.sample(problem, nsamples)

param_names = list(default_values.keys())
sobol_samples = pd.DataFrame(sobol_samples, columns=param_names)

#Save output
sobol_samples.to_csv('data_output/sobol_samples.csv', index=False)