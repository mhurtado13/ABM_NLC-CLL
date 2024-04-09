import pandas as pd
import sys
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
from model_simulation import run_model

num_tasks = int(sys.argv[1])
n_replicates = int(sys.argv[2])

pool = ThreadPool(num_tasks) 

input = {'uptake_rate_cancer': 1.0, 'speed_cancer': 1.0, 'transformation_rate_cancer': 5e-5,
                  'speed_monocytes':1.0, 'dead_phagocytosis_rate_monocytes':25e-2, 'speed_macrophages':1.0,
                  'dead_phagocytosis_rate_macrophages':92e-2, 'secretion_rate_NLCs':1.0, 'speed_NLCs':1.0,
                  'dead_phagocytosis_rate_NLCs':4e-2}

#death rate apoptotic cells
#number of initial apoptotic cells 
#number of initial CLL cells

default_values = list(input.values())

explore_values = [0, 1, 3, 5, 7, 9, 10]

def reset_values(data, values_def):        
    for i, key in enumerate(data.keys()):
        data[key] = values_def[i]

results = []
for parameter in input.keys():
    x = []
    for i in explore_values:
        input[parameter] = i
        x.append(tuple(input.values()))
        reset_values(input, default_values)
    
    thread_params = []
    if num_tasks >= len(explore_values):
        for thread_id, param in zip(range(num_tasks), x):
            thread_params.append((thread_id,) + param)
    else:
        for i, param in enumerate(x):
            thread_id = i % num_tasks + 1
            thread_params.append((thread_id,) + param)

    params = [(("config/NLC_CLL.xml", n_replicates) + thread_params[contador]) for contador in range(len(explore_values))]
    res = pool.starmap(run_model, params)
    results.extend(res)

pool.close()
pool.join()

print("Pool closed")
print("Everything done! Results are saved in the ./data_output folder")

#Initialize viability and concentration vectors with first results
viability = results[0][0]
concentration = results[0][1]

for i in range(1, len(results)):
    via, conc = results[i]
    viability = pd.concat([viability, via], axis=1, ignore_index=True) #concatenating in the same order as explore_values
    concentration = pd.concat([concentration, conc], axis=1, ignore_index=True) #concatenating in the same order as explore_values

viability.to_csv('data_output/viability_exploration.csv', index=False, header=True)
concentration.to_csv('data_output/concentration_exploration.csv', index=False, header=True)