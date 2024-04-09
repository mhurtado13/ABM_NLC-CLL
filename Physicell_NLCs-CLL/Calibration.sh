#!/bin/bash

# Define the number of tasks running in parallel
NUM_TASKS=2

# Define the number replicates for bootstrapping 
NUM_REPLICATES=2

# Define the population size for genetic algorithm
POP_SIZE=3

# Define the number of generations for genetic algorithm
NUM_GENERATION=4

# Calibration of Physicell model using NSGA-II
python scripts/param_calibration.py $NUM_TASKS $NUM_REPLICATES $POP_SIZE $NUM_GENERATION
