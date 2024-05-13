#!/bin/bash
#SBATCH --job-name=NLC-CLL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=22
#SBATCH --mem=128G
#SBATCH --partition=workq
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=marcelo.hurtado@inserm.fr
#SBATCH -o /home/mhurtado/work/ABM_NLC-CLL/logs/%x.o
#SBATCH -e /home/mhurtado/work/ABM_NLC-CLL/logs/%x.e

# Define the number of tasks running in parallel
NUM_TASKS=22

# Define the number replicates for bootstrapping 
NUM_REPLICATES=5

# Parameter exploration
python scripts/param_exploration.py $NUM_TASKS $NUM_REPLICATES 
