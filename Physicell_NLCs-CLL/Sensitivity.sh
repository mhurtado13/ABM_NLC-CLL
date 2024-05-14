#!/bin/bash
#SBATCH --job-name=NLC-CLL-Sensitivity
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=100
#SBATCH --mem=128G
#SBATCH --partition=workq
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=marcelo.hurtado@inserm.fr
#SBATCH -o /home/mhurtado/work/ABM_NLC-CLL_cluster/logs/Sensitivity/%x.o
#SBATCH -e /home/mhurtado/work/ABM_NLC-CLL_cluster/logs/Sensitivity/%x.e

# Define the number of samples to generate for the Sobol analysis
NUM_SAMPLES=100 #Sobol: N*(2D + 2)

# Define the number of nodes used to parallelize the analysis
NUM_TASKS=100

# Define the number replicates for bootstrapping 
NUM_REPLICATES=10

# Run param_sensitivity.py script
python scripts/param_sensitivity.py $NUM_SAMPLES $NUM_TASKS $NUM_REPLICATES
