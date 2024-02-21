#!/bin/bash

# Define the paths to the input XML file and the C++ software executable
INPUT="./config/NLC_CLL.xml"

# Define the number of samples to generate for the Sobol analysis
NUM_SAMPLES=128

# Define the number of nodes used to parallelize the analysis
NUM_NODES=12

# Generate the samples using a Python script
python scripts/sampling.py $NUM_SAMPLES

# Split the sample so that you can run multiple instances on different nodes
python scripts/subspaces.py $NUM_NODES

# Loop over the LHS samples and run Physicell with each parameter set
python scripts/xml_parse.py $INPUT $NUM_NODES
