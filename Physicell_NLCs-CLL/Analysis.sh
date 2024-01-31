#!/bin/bash

# Define the paths to the input XML file and the C++ software executable
INPUT = "./config/template.xml"

# Define the number of samples to generate for the LHS analysis
NUM_SAMPLES = 20

# Define the number of nodes used to parallelize the analysis
NUM_NODES = 3

# Generate the samples using a Python script
python lhs_sampling.py ${NUM_SAMPLES}

# Split the sample so that you can run multiple instances on different nodes
python generate_subspaces.py ${NUM_NODES}

# Loop over the LHS samples and run Physicell with each parameter set
python parser.py ${INPUT}