import numpy as np
import ROOT 
from ROOT import TBrowser
import json
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path

'''''
'''''

### So in this project I am going to intake all the jason data. Then go through all the channels and the samples inside the channels. 
### This time its going to be simple. Just make a 96 root histogram files and put them into a single directory



# Opening JSON file


f = open('/Users/amanpritam/Downloads/mA50.json')               ### here we write the pathname of the json file

ch_n = []
s_n = []
bin_numbers = []
mod_n = []

data = json.load(f)
channels = pd.DataFrame(data['channels'])
#print(channels['name'])

s=channels['samples']


observation = pd.DataFrame(data['observations'])




mod_DOWN ={}
mod_UP ={}


for j in range(len(s)):
  for i in range(len(s[j])):

    channel_name = channels['name'][j]
    name_sample = s[j][i]['name']
    data_sample = s[j][i]['data']
    #print('Channel Name: ',channel_name)
    #print('Sample Name: ',name_sample)
    #print('Data Sample: ',data_sample,'\n')
    
    ch_n.append(channel_name)                              ### These 3 give channel name, sample name and data. 
    s_n.append(name_sample)                                ### Even though there are 6 channels as the index corresponds to a specific sample
    bin_numbers.append(data_sample)
    entry_data_UP = {}
    entry_data_DOWN = {}


    for k in range(len(s[j][i]["modifiers"])):
      name_mod = s[j][i]["modifiers"][k]["name"]
      mod_n.append(name_mod)
      type_mod = s[j][i]["modifiers"][k]["type"]


      if type_mod == "staterror":
                                          
        hi_data_hist = s[j][i]["modifiers"][k]["data"] 
        #lo_data_hist = np.nan                             

      elif type_mod == 'normsys':

        lo_data_mod = s[j][i]["modifiers"][k]["data"]["lo"]
        lo_data_hist = [h*lo_data_mod for h in data_sample]
        hi_data_mod = s[j][i]["modifiers"][k]["data"]["hi"]
        hi_data_hist = [h*hi_data_mod for h in data_sample]
      

      #elif type_mod == 'normfactor':
       # hi_data_hist = np.nan
        #hi_data_hist = s[j][i]["modifiers"][k]["data"]
        #lo_data_hist = np.nan

      #elif type_mod == 'lumi':
       # hi_data_hist = np.nan
        #hi_data_hist = s[j][i]["modifiers"][k]["data"]
        #lo_data_hist = np.nan

      elif type_mod == "histosys":
        lo_data_hist = s[j][i]["modifiers"][k]["data"]["lo_data"]
        hi_data_hist = s[j][i]["modifiers"][k]["data"]["hi_data"]
      
      else:
        hi_data_hist = [1e-10,1e-10,1e-10]
        lo_data_hist = [1e-10,1e-10,1e-10]

      entry_data_UP[f'{name_mod}_UP'] = hi_data_hist
      entry_data_DOWN[f'{name_mod}_DOWN'] = lo_data_hist
      
    mod_UP[f'{name_sample}'] = entry_data_UP
    mod_DOWN[f'{name_sample}'] = entry_data_DOWN





name_l = []

for i in range(len(s_n)):

    # Open or create a ROOT file
    desktop_path = os.path.join(os.path.expanduser("~"), "Documents/Root_Project_1/Project_2")    ## The path of the files is in documents/atlas projects/ project 2,
    
                                                                                                  ## Appropriate directories are needed for the code to work, or can tweak the directory path.
    # Move the file to the desktop
    output_file = ROOT.TFile(os.path.join(desktop_path, f'histograms_{s_n[i]}.root'), "RECREATE")

    histogram = ROOT.TH1D(f'h_{ch_n[i]}', f'h_{ch_n[i]}', 3, -0.5, 2.5)
    for var in range(0,3):
      histogram.SetBinContent(var+1,bin_numbers[i][var])

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
      hist_d.SetBinContent(0,lsdo_val[d][0])
      hist_d.SetBinContent(1,lsdo_val[d][1])
      hist_d.SetBinContent(2,lsdo_val[d][2])
      
      hist_u = ROOT.TH1D(f'h_{ch_n[i]}_{lsup_key[d]}',f'h_{ch_n[i]}_{lsup_key[d]}',3,-0.5, 2.5)
      hist_u.SetBinContent(0,lsup_val[d][0])
      hist_u.SetBinContent(1,lsup_val[d][1])
      hist_u.SetBinContent(2,lsup_val[d][2])
      output_file.Write()
      #for var in range(0,3):
       # hist_d.SetBinContent(var+1,lsdo_val[d][var])

    #for u in range(len(lsup_key)):
     # hist_u = ROOT.TH1D(f'h_{lsup_key[u]}',f'Histogram_{lsup_key[u]}',3,-0.5, 2.5)
     # hist_u.SetBinContent(0,lsup_val[d][0])
     # hist_u.SetBinContent(1,lsup_val[d][1])
     # hist_u.SetBinContent(2,lsup_val[d][2])
      #for var in range(0,3):
      #  hist_u.SetBinContent(var+1,lsup_val[d][var])



output_file.Close()

for i in range(len(observation)):

    # Open or create a ROOT file
    desktop_path = os.path.join(os.path.expanduser("~"), "Documents/ATLAS_projects/Project_2")
    output_file_1 = ROOT.TFile(os.path.join(desktop_path, f'histograms_{observation["name"][i]}_data.root'), "RECREATE")

    histogram_1 = ROOT.TH1D(f'h_{observation["name"][i]}', f'h_{observation["name"][i]}', 3, -0.5, 2.5)
    for var in range(0,3):
      histogram_1.SetBinContent(var+1,observation['data'][i][var])
    output_file_1.Write()

    output_file_1.Close()

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