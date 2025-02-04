import configparser
import os
import lib.jag3dBatchLib as bf
import pandas as pd

import lib.PyGeoCom_Punktmessung as gc

if __name__ == "__main__":
    # Read Settings from config file
    config = configparser.ConfigParser()
    config.sections()
    config.read("config_tachy.ini")

    totalstationMeasurementPath = config.get("Output", "path")
    turnOff = config.getboolean("Misc", "turnOff")
    twoFace = config.getboolean("Misc", "twoFace")
    pktListPath = config.get("Input", "path")
    hasHeader = config.getboolean("Input", "hasHeader")

    lamb = config.getint("ATM", "lambda")
    pres = config.getfloat("ATM", "pressure")
    temp = config.getfloat("ATM", "temp")
    serialPort = config.get("Serial", "port")
    baudRate = config.get("Serial", "baudRate")

    ## Start totalstation measurement
    measurementFileName = gc.StartTachyMeasurement(
        totalstationMeasurementPath,
        pktListPath,
        turnOff,
        twoFace,
        hasHeader,
        lamb,
        pres,
        temp,
        serialPort,
        baudRate,
    )

    config.read("config_jag.ini")
    enginePath = config.get("JAG", "enginePath")
    controlEpochFilePath = config.get("JAG", "controlPath")
    # create control epoch file from measurement file
    bf.jag_input_format_parser(measurementFileName, controlEpochFilePath)

    projectName = config.get("JAG", "projectName")

    databasePath = f"jdbc:hsqldb:file:{os.getcwd()}{projectName}"
    groups = bf.CheckGroups(databasePath, os.getcwd() + enginePath)
    groups_type_nr = groups.astype(str)
    """
    type    Observation
    1       Leveling data
    2       Direction sets
    3       Horizontal distances
    4       Slope distances
    5       Zenith angles
    """
    filePathDatumPoints = config.get("Start", "datumPointFile")
    filePathObjectPoints = config.get("Start", "objectPointFile")
    filePathControlEpoch = f"{controlEpochFilePath}/obs_c.txt"

    queries = bf.createQueries(
        groups_type_nr, filePathDatumPoints, filePathObjectPoints, filePathControlEpoch
    )

    # Write new measurements to JAG3D-database
    bf.WriteDatabase(queries, databasePath, enginePath)

    bf.JAG_Execute(os.getcwd() + projectName)  # starts JAG3D adjustment via Shell
    
    [PktApost, PktID, ObjApost, ObjID, globaltest] = bf.ReadDatabase(
        databasePath, enginePath
    )  # Reads results from JAG3D database
    
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