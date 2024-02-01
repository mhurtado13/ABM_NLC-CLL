import pandas as pd
import os

df = pd.read_csv('../data_output/data.csv')

#####Viability

# Calculate the column-wise median
num_lis = []
for i in range(1, df.shape[1],2):
    number = df.iloc[:, i]
    num_lis.append(number)
    
num_lis = pd.DataFrame(num_lis)
medians = num_lis.median()

# Create a new DataFrame with the averages
viability = pd.Series(medians, name = "viability")
viability_csv = '../data_output/viability.csv'

if os.path.exists(viability_csv):
    old_data = pd.read_csv(viability_csv)
    new_data = pd.concat([old_data, viability], axis=1)
    new_data.to_csv(viability_csv, index=False, header=True)
else:
    viability.to_csv(viability_csv, index=True, header=True)


#####Concentration
    
# Calculate the column-wise median
num_lis = []
for i in range(2, df.shape[1],2):
    number = df.iloc[:, i]
    num_lis.append(number)
    
num_lis = pd.DataFrame(num_lis)
medians = num_lis.median()

# Create a new DataFrame with the averages
concentration = pd.Series(medians, name = "concentration")
concentration_csv = '../data_output/concentration.csv'

if os.path.exists(concentration_csv):
    old_data = pd.read_csv(concentration_csv)
    new_data = pd.concat([old_data, concentration], axis=1)
    new_data.to_csv(concentration_csv, index=False, header=True)
else:
    concentration.to_csv(concentration_csv, index=True, header=True)


