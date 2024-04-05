#!/bin/bash

# Define the parameter to change: 
#- 'uptake_rate_cancer'
#- 'speed_cancer'
#- 'transformation_rate_cancer'
#- 'speed_monocytes'
#- 'dead_phagocytosis_rate_monocytes'
#- 'speed_macrophages'
#- 'dead_phagocytosis_rate_macrophages'
#- 'secretion_rate_NLCs'
#- 'speed_NLCs'
#- 'dead_phagocytosis_rate_NLCs'

# Define the number of tasks running in parallel
NUM_THREADS=2

# Define the number replicates for bootstrapping 
NUM_REPLICATES=2

# Parameter exploration
python scripts/param_exploration.py $NUM_THREADS $NUM_REPLICATES 
