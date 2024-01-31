#!/bin/bash

# Define the paths to the input XML file and the C++ software executable
INPUT = "./config/NLC_CLL.xml"

# Define the number of samples to generate for the LHS analysis
NUM_SAMPLES = 3

# Define the number of nodes used to parallelize the analysis
NUM_NODES = 3

# Generate the samples using a Python script
python sampling.py ${NUM_SAMPLES}

# Split the sample so that you can run multiple instances on different nodes
python subspaces.py ${NUM_NODES}

# Loop over the LHS samples and run Physicell with each parameter set
python xml_parse.py ${INPUT}
