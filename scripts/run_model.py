import xml.etree.ElementTree as ET
import random
import subprocess
from collect_data import collect_data
import pandas as pd
import sys

iterations = int(sys.argv[1])

xml_file = "config/NLC_CLL.xml"
output_directory = "output/"
tree = ET.parse(xml_file) #Load original xml file
root = tree.getroot()

command = ["./project", xml_file]
param_element = root.find(".//random_seed") #Find the random seed in XML file
param_element.text = str(random.randint(0,4294967295))
results = []

## Running model
for i in range(iterations):
    print("Running NLC-CLL model iteration " + str(i+1) + "\n")
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        stdout, stderr = proc.communicate()
    res = collect_data(output_directory, xml_file)
    results.append(res)

## Collecting data
print("Collecting data from iterations" + "\n")
viability, concentration, monocytes, macrophages, NLCs = results[0]
for i in range(1, len(results)):
    via, conc, mono, macro, nlc = results[i]
    viability = pd.concat([viability, via], axis = 1, ignore_index=True)
    concentration = pd.concat([concentration, conc], axis = 1, ignore_index=True)
    monocytes = pd.concat([monocytes, mono], axis = 1, ignore_index=True)
    macrophages = pd.concat([macrophages, macro], axis = 1, ignore_index=True)
    NLCs = pd.concat([NLCs, nlc], axis = 1, ignore_index=True)

## Save files
print("Files are saved in data/ directory" + "\n")
viability_name = f'data/Viability_results.csv'
concentration_name = f'data/Concentration_results.csv'
monocytes_name = f'data/Monocytes_results.csv'
macrophages_name = f'data/Macrophages_results.csv'
nlc_name = f'data/NLCs_results.csv'

viability.to_csv(viability_name, index=False, header=True)
concentration.to_csv(concentration_name, index=False, header=True)
monocytes.to_csv(monocytes_name, index=False, header=True)
macrophages.to_csv(macrophages_name, index=False, header=True)
NLCs.to_csv(nlc_name, index=False, header=True)
