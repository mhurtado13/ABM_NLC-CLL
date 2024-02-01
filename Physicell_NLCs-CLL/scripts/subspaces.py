
import pandas as pd 
import sys

num_files = int(sys.argv[1])

data = pd.read_csv('../data_output/lhs_samples.csv')

rows = int(len(data)/num_files)

# Loop over the number of output files to generate
for i in range(num_files):
    # Calculate the start and end indices for the current output file
    start_idx = i * rows
    end_idx = (i + 1) * rows

    # If this is the last file, include any remaining rows
    if i == num_files - 1:
        end_idx = len(data)

    # Extract the rows for the current output file
    subset = data.iloc[start_idx:end_idx]

    # Write the rows to a new CSV file
    filename = f'../data_output/lhs_samples_{i}.csv'
    subset.to_csv(filename, index=False)