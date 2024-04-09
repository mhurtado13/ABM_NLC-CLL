#!/bin/bash

# Define the number of samples to generate for the Sobol analysis
NUM_SAMPLES=2 #Sobol: N*(2D + 2)

# Define the number of nodes used to parallelize the analysis
NUM_TASKS=2

# Define the number replicates for bootstrapping 
NUM_REPLICATES=2

# Run param_sensitivity.py script
python scripts/param_sensitivity.py $NUM_SAMPLES $NUM_TASKS $NUM_REPLICATES
