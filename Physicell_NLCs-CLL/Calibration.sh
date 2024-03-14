#!/bin/bash

# Define the population size for genetic algorithm
POP_SIZE=500

# Define the number of tasks running in parallel
NUM_THREADS=8

# Define the number replicates for bootstrapping 
NUM_REPLICATES=50

# Calibration of Physicell model using NSGA-II
python scripts/calibration.py $POP_SIZE $NUM_THREADS $NUM_REPLICATES
