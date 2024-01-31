data = pd.read_csv('lhs_samples.csv')
num_files = 4
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
    filename = f'saltelli_samples_{i}.csv'
    subset.to_csv(filename, index=False)