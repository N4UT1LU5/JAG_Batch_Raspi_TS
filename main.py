import configparser
import pandas as pd
import os

import lib.jag3dBatchLib as bf


config = configparser.ConfigParser()
config.sections()
config.read("config_jag.ini")

projectName = config.get("JAG", "projectName")
enginePath = config.get("JAG", "enginePath")
databasePath = f"jdbc:hsqldb:file:{os.getcwd()}{projectName}"

# Set Java Path environment variable
jag3dPath = "JagEngine"
java_path = rf"{os.getcwd()}\{jag3dPath}\openjdk\bin"
os.environ["PATH"] = java_path
os.environ["JAVA_HOME"] = java_path
#print(os.environ["JAVA_HOME"])
#subprocess.run("java -version", shell=True)


## Read start data
filePathDatumPoints = config.get("Start", "datumPointFile")
filePathObjectPoints = config.get("Start", "objectPointFile")

## Read oberservation data from control epoch
controlEpoch_df = pd.read_csv(r'data\controlEpoch\obs_c.txt', delimiter='\t', header=None, skipinitialspace=True, names= ['StID','TarID','group_id_txt','Val'])

## Get the JAG3D groups
groups = bf.CheckGroups(databasePath, os.getcwd() + enginePath)
groups_type_nr = groups.astype(str)

## Create quereies to update the JAG3D database
queries = bf.createQueries(
    groups_type_nr, filePathDatumPoints, filePathObjectPoints, controlEpoch_df
)

## Write new obs in the database
bf.WriteDatabase(queries,databasePath,enginePath)

## Execute JAG3D Batch
bf.JAG_Execute(os.getcwd() + projectName,rf"{os.getcwd()}\{jag3dPath}")

## Read database after alligment
[PktApost, PktID, ObjApost, ObjID, globaltest] = bf.ReadDatabase(databasePath,enginePath)

## summary of results
objPoints = pd.merge(ObjID, ObjApost, on="ID")
objPoints["Typ"] = "Obj"
datPoints = pd.merge(PktID, PktApost, on="ID")
datPoints["Typ"] = "Dat"
datPoints = datPoints[
    datPoints["Tprio"] != 0
]  
# Filter the object points
result = pd.concat([datPoints, objPoints])
result = result.drop(columns=["ID"])
print(f'S0_2:{globaltest}')
print(result)
