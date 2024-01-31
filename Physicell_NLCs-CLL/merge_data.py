import pandas as pd
import os

df = pd.read_csv('data.csv')

# Calculate the column-wise median
medians = df.median()

# Create a new DataFrame with the averages
medians_df = pd.DataFrame(medians).T
output_csv = 'output.csv'
# Write the averages DataFrame to a new CSV file
medians_df.to_csv('averages.csv', index=False)

if os.path.exists(output_csv):
    old_data = pd.read_csv(output_csv)
    new_data = pd.concat([old_data, medians_df], axis=0, ignore_index=True)
    new_data.to_csv(output_csv, index=False, header=True)
else:
    medians_df.to_csv(output_csv, index=False, header=True)