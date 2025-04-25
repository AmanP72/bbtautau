import numpy as np
import ROOT 
from ROOT import TBrowser
import json
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path
from collections import Counter, defaultdict



# Opening JSON file


#f = open('/Users/amanpritam/Documents/Root_Project_1/mA60_combined.json')               ###   <-----   Change File Path here for different mass
f1 = open('/Users/amanpritam/Documents/Root_Project_1/mA25_emu.json')
f2 = open('/Users/amanpritam/Documents/Root_Project_1/mA25_lephad.json')



ch_n = []
s_n = []
bin_numbers = []
mod_n = []
empty_nominal = []


#data = json.load(f)

data1 = json.load(f1)
data2 = json.load(f2)



channels1 = pd.DataFrame(data1['channels'])
channels2 = pd.DataFrame(data2['channels'])
channels = pd.concat([channels1, channels2], ignore_index=True)

#channels = pd.DataFrame(data['channels'])


#print(channels['name'])

s=channels['samples']


#observation = pd.DataFrame(data['observations'])

observation1 = pd.DataFrame(data1['observations'])
observation2 = pd.DataFrame(data2['observations'])
observation = pd.concat([observation1, observation2], ignore_index=True)



mod_DOWN ={}
mod_UP ={}
staterror = {}

for j in range(len(s)):
  for i in range(len(s[j])):


    channel_name = channels['name'][j]
    name_sample = s[j][i]['name']
    data_sample = s[j][i]['data']
    #print('Channel Name: ',channel_name)
    #print('Sample Name: ',name_sample)
    #print('Data Sample: ',data_sample,'\n')

    if data_sample[0] == 1e-10 and data_sample[1] == 1e-10 and data_sample[2] == 1e-10:  ### Removing the empty samples
      empty_nominal.append(channel_name)

    else:

      #print(s[0][i]['name'])
      ch_n.append(channel_name)
      s_n.append(name_sample)
      bin_numbers.append(data_sample)

      ### Dictionary functions for modifiers
      entry_data_UP = {}
      entry_data_DOWN = {}


      
      for k in range(len(s[j][i]["modifiers"])):
        name_mod = s[j][i]["modifiers"][k]["name"]
        mod_n.append(name_mod)
        type_mod = s[j][i]["modifiers"][k]["type"]

        if type_mod == "staterror":

          staterror[f'{name_sample}'] = s[j][i]["modifiers"][k]["data"]   ## This is to get the staterror data so we can use it later to add to the histograms


        elif type_mod == 'normsys':

          lo_data_mod = s[j][i]["modifiers"][k]["data"]["lo"]
          lo_data_hist = [h*lo_data_mod for h in data_sample]
          hi_data_mod = s[j][i]["modifiers"][k]["data"]["hi"]
          hi_data_hist = [h*hi_data_mod for h in data_sample]
          entry_data_UP[f'{name_mod}_UP'] = hi_data_hist
          entry_data_DOWN[f'{name_mod}_DOWN'] = lo_data_hist


        elif type_mod == "histosys" and 'gamafactor' not in name_mod:
          lo_data_hist = s[j][i]["modifiers"][k]["data"]["lo_data"]
          hi_data_hist = s[j][i]["modifiers"][k]["data"]["hi_data"]
          entry_data_UP[f'{name_mod}_UP'] = hi_data_hist
          entry_data_DOWN[f'{name_mod}_DOWN'] = lo_data_hist


      if entry_data_UP:
          mod_UP[name_sample] = entry_data_UP
      if entry_data_DOWN:
          mod_DOWN[name_sample] = entry_data_DOWN



### this piece of code is meant to deal with the gamafactors and just getting one set  ###




# Extract all samples
samples = [s['samples'] for s in channels.to_dict('records')]
samples = [item for sublist in samples for item in sublist]

# Initialize a dictionary to store gamafactor data by sample
gamafactor_data_by_sample = defaultdict(lambda: {'lo_data': [], 'hi_data': []})

# Extract gamafactor modifiers
for sample in samples:
    sample_name = sample.get('name')
    data_sample = sample.get('data', [])
    # Check if all bins are 1e-10 (empty sample)
    if all(value == 1e-10 for value in data_sample):
        # Skip this sample if all bins are empty
        continue

    modifiers = sample.get('modifiers', [])
    for mod in modifiers:
        if 'gamafactor' in mod['name']:
            lo_data = mod['data'].get('lo_data', [])
            hi_data = mod['data'].get('hi_data', [])
            if lo_data and hi_data and len(lo_data) == len(hi_data):
                gamafactor_data_by_sample[sample_name]['lo_data'].append(lo_data)
                gamafactor_data_by_sample[sample_name]['hi_data'].append(hi_data)

# Function to find unique elements or use the most common element
def find_unique_or_common_elements(data_list):
    if not data_list:
        return []
    
    # Determine the number of bins (assumed to be consistent across all lists)
    num_bins = len(data_list[0])
    
    # Organize elements by bin
    bins = [[] for _ in range(num_bins)]
    
    for data in data_list:
        for bin_index in range(num_bins):
            bins[bin_index].append(data[bin_index])
    
    unique_elements = []
    
    for bin_index in range(num_bins):
        bin_elements = bins[bin_index]
        bin_count = Counter(bin_elements)
        bin_most_common = bin_count.most_common(1)[0][0]
        
        # Collect unique elements or use the most common element
        unique_bin_elements = [item for item in bin_elements if bin_count[item] == 1]
        if not unique_bin_elements:
            unique_bin_elements = [bin_most_common] #* len(data_list)
        unique_elements.extend(unique_bin_elements)
    
    return unique_elements

# Prepare the final result dictionary
result = {}

for sample_name, data in gamafactor_data_by_sample.items():
    lo_data = data['lo_data']
    hi_data = data['hi_data']
    
    # Find unique or most common elements
    unique_lo = find_unique_or_common_elements(lo_data)
    unique_hi = find_unique_or_common_elements(hi_data)
    
    result[sample_name] = (unique_lo, unique_hi)

###---------------------------------------------------------###



name_l = []

for i in range(len(s_n)):
    
    #bin_err = staterror[f'{s_n[i]}']

    gamabinerror = []
    for k in range(3):
        gamabinerror.append(abs(result[s_n[i]][0][k]-result[s_n[i]][1][k])/2)

    # Open or create a ROOT file
    desktop_path = os.path.join(os.path.expanduser("~"), "Documents/Root_Project_1/mA25_hist_combined")    ###   <-----   Change File Path here for different mass
    
                                                                                                  ## Appropriate directories are needed for the code to work, or can tweak the directory path.
    # Move the file to the desktop
    output_file = ROOT.TFile(os.path.join(desktop_path, f'histograms_{s_n[i]}.root'), "RECREATE")

    histogram = ROOT.TH1D(f'h_{ch_n[i]}', f'h_{ch_n[i]}', 3, -0.5, 2.5)
    for var in range(0,3):
      histogram.SetBinContent(var+1,bin_numbers[i][var])
      histogram.SetBinError(var+1,gamabinerror[var])
      #histogram.SetBinError(var+1,bin_err[var])

    output_file.Write()  
    output_file.Close()


    lsdo_val = []
    lsdo_key = []
    lsup_val = []
    lsup_key = []
    for l in mod_DOWN[f'{s_n[i]}'].values():
      lsdo_val.append(l)
    for k in mod_DOWN[f'{s_n[i]}'].keys():
      lsdo_key.append(k)

    for lu in mod_UP[f'{s_n[i]}'].values():
      lsup_val.append(lu)
    for ku in mod_UP[f'{s_n[i]}'].keys():
      lsup_key.append(ku)
    
    output_file = ROOT.TFile(os.path.join(desktop_path, f'histograms_{s_n[i]}.root'), "UPDATE")


    for d in range(len(lsdo_key)):
      hist_d = ROOT.TH1D(f'h_{ch_n[i]}_{lsdo_key[d]}',f'h_{ch_n[i]}_{lsdo_key[d]}',3,-0.5, 2.5)
      for  var_d in range(0,3):
        hist_d.SetBinContent(var_d+1,lsdo_val[d][var_d])
      #hist_d.SetBinContent(0,lsdo_val[d][0])
      #hist_d.SetBinContent(1,lsdo_val[d][1])
      #hist_d.SetBinContent(2,lsdo_val[d][2])
      
      hist_u = ROOT.TH1D(f'h_{ch_n[i]}_{lsup_key[d]}',f'h_{ch_n[i]}_{lsup_key[d]}',3,-0.5, 2.5)
      for  var_u in range(0,3):
        hist_u.SetBinContent(var_u+1,lsup_val[d][var_u])
      #hist_u.SetBinContent(0,lsup_val[d][0])
      #hist_u.SetBinContent(1,lsup_val[d][1])
      #hist_u.SetBinContent(2,lsup_val[d][2])
      output_file.Write()
      #for var in range(0,3):
       # hist_d.SetBinContent(var+1,lsdo_val[d][var])





output_file.Close()


# Open or create a ROOT file
desktop_path = os.path.join(os.path.expanduser("~"), "Documents/Root_Project_1/mA25_hist_combined")    ###   <-----   Change File Path here for different mass
output_file_1 = ROOT.TFile(os.path.join(desktop_path, f'histograms_data.root'), "RECREATE")
for i in range(len(observation)):
  histogram_1 = ROOT.TH1D(f'h_{observation["name"][i]}', f'h_{observation["name"][i]}', 3, -0.5, 2.5)
  for var in range(0,3):
    histogram_1.SetBinContent(var+1,observation['data'][i][var])
  output_file_1.Write()



output_file_1.Close()
print('done')




    


    #histogram.SetBinContent(1,bin_numbers[i][0])
    #histogram.SetBinContent(2,bin_numbers[i][1])
    #histogram.SetBinContent(3,bin_numbers[i][2])
    
    #name_hist = f'Hisotgrams_{s_n[i]}'
    #print(f'Hisotgrams_{s_n[i]}')
    #name_l.append(name_hist)
    #np.savetxt(f"{desktop_path}/Hisotgrams_{s_n[i]}.txt",bin_numbers)
    #print(i)

# Create a directory within the ROOT file