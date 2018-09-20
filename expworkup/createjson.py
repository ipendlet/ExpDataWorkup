#Copyright (c) 2018 Ian Pendleton - MIT License
import json
from pathlib import Path
from expworkup import googleio
import os
import pandas as pd
import numpy as np
import time

## Set the workflow of the code used to generate the experimental data and to process the data
WorkupVersion=1.0

def Expdata(DatFile):
    ExpEntry=DatFile
    with open(ExpEntry, "r") as file1:
        file1out=json.load(file1)
        lines=(json.dumps(file1out, indent=4, sort_keys=True))
    lines=lines[:-8]
    return(lines)
    ## File processing for the experimental JSON to convert to the final form (header of the script)

def Robo(robotfile):
    #o the file handling for the robot.xls file and return a JSON object
    robo_df = pd.read_excel(open(robotfile,'rb'), sheet_name=0,usecols=7)
    robo_df_2 = pd.read_excel(open(robotfile,'rb'), sheet_name=0,usecols=(8,9)).dropna()
    robo_df_3 = pd.read_excel(open(robotfile,'rb'), sheet_name=0,usecols=(10,11,12,13)).dropna()
    robo_dump=json.dumps(robo_df.values.tolist())
    robo_dump2=json.dumps(robo_df_2.values.tolist())
    robo_dump3=json.dumps(robo_df_3.values.tolist())
    return(robo_dump, robo_dump2, robo_dump3)

def Crys(crysfile):
    ##Gather the crystal datafile information and return JSON object
    headers=crysfile.pop(0)
    crys_df=pd.DataFrame(crysfile, columns=headers)
    crys_df_curated=crys_df[['Concatenated Vial site', 'Crystal Score']]
    crys_list=crys_df_curated.values.tolist()
    crys_dump=json.dumps(crys_list)
    return(crys_dump)

def genthejson(Outfile, workdir, opfolder, drive_data):
    ## Do all of the file handling for a particular run and assemble the JSON, return the completed JSON file object
    ## and location for sorting and final comparison
    Crysfile=drive_data
    Expdatafile=workdir+opfolder+'_ExpDataEntry.json'
    Robofile=workdir+opfolder+'_RobotInput.xls'
    exp_return=Expdata(Expdatafile)
    robo_return=Robo(Robofile)
    crys_return=Crys(Crysfile)
    print(exp_return, file=Outfile)
    print('\t},', file=Outfile)
    print('\t', '"well_volumes":', file=Outfile)
    print('\t', robo_return[0], ',', file=Outfile)
    print('\t', '"tray_environment":', file=Outfile)
    print('\t', robo_return[1], ',', file=Outfile)
    print('\t', '"robot_reagent_handling":', file=Outfile)
    print('\t', robo_return[2], ',', file=Outfile)
    print('\t', '"crys_file_data":', file=Outfile)
    print('\t', crys_return, file=Outfile)
    print('}', file=Outfile)

def ExpDirOps(myjsonfolder):
    ##Call code to get all of the relevant folder titles from the experimental directory and
    ##Cross reference with the working directory of the final Json files send the list of jobs needing processing
    ## loops of IFs for file checking
    opdir='13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B'
    ExpList = googleio.drivedatfold(opdir)
    crys_dict=(ExpList[0])
    robo_dict=(ExpList[1])
    Expdata=(ExpList[2])
    dir_dict=(ExpList[3])
    for folder in dir_dict:
        exp_json=Path(myjsonfolder+"/%s.json" %folder)
        if exp_json.is_file():
            print(folder, 'exists')
        else:
            Outfile=open(exp_json, 'w')
            workdir='data/datafiles/'
            print('%s Created' %folder)
            data_from_drive= googleio.getalldata(crys_dict[folder],robo_dict[folder],Expdata[folder], workdir, folder)
            genthejson(Outfile, workdir, folder, data_from_drive)
            Outfile.close()
            time.sleep(2) #due to the limitations of the haverford googleapi we have to throttle the connection a bit to limit the number of api requests anything lower than 2 bugs it out