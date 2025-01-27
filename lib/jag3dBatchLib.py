import pandas as pd
import subprocess
import jaydebeapi
import numpy as np

RHO = 200 / np.pi

# ConnectDatabase
def ConnectDatabase(databasePath, enginePath):
    # Connects to HyperSQL-database
    # databasePath = path of JAG3D-project
    # enignePath = installation-path of hsqldb.jar
    # hsqldb-2.7.2: Download  https://sourceforge.net/projects/hsqldb/files/hsqldb/hsqldb_2_7/ and open zip
    driverPath = "org.hsqldb.jdbc.JDBCDriver"
    credentials = ["SA", ""]

    # conntect to JAG3D-database (HyperSQL)
    connection = jaydebeapi.connect(driverPath, databasePath, credentials, enginePath)

    return connection

# Function to execute the alligment in Terminal
def JAG_Execute(projectName, jag3dPath):
    # if you want no output in the terminal --> change TRUE to FALSE
    cmd = rf"java -cp {jag3dPath}\jag3d.jar org.applied_geodesy.adjustment.cmd.OpenAdjustmentCMD {projectName} TRUE"
    print(cmd)
    subprocess.run(cmd, shell=True)
    return


# ReadDatabase
def ReadDatabase(databasePath, enginePath):
    # Read results from adjustment
    try:
        conn = ConnectDatabase(databasePath, enginePath)
        curs = conn.cursor()

        ## datum points
        # OpenAdjustment"."PointAposteriori" (point coordinates)
        query1 = 'SELECT "id", "gross_error_x", "gross_error_y", "gross_error_z", "t_prio", "significant" FROM "OpenAdjustment"."PointAposteriori"'
        curs.execute(query1)
        PktApost = curs.fetchall()
        PktApost = pd.DataFrame(
            PktApost, columns=["ID", "dX", "dY", "dZ", "Tprio", "Sig"]
        )

        # OpenAdjustment"."PointAprori" (for point-id's of datum points)
        query2 = 'SELECT "id", "name" FROM "OpenAdjustment"."PointApriori"'
        curs.execute(query2)
        PktID = curs.fetchall()
        PktID = pd.DataFrame(PktID, columns=["ID", "Pkt"])

        ## object points
        # OpenAdjustment"."CongruenceAnalysisPointPairAposteriori" (point nexus object points)
        query3 = 'SELECT "id", "x", "y", "z", "t_prio", "significant" FROM "OpenAdjustment"."CongruenceAnalysisPointPairAposteriori"'
        curs.execute(query3)
        ObjApost = curs.fetchall()
        ObjApost = pd.DataFrame(
            ObjApost, columns=["ID", "dX", "dY", "dZ", "Tprio", "Sig"]
        )

        # OpenAdjustment"."CongruenceAnalysisPointPairApriori" (for ids of point nexus)
        query4 = 'SELECT "id", "start_point_name" FROM "OpenAdjustment"."CongruenceAnalysisPointPairApriori"'
        curs.execute(query4)
        ObjID = curs.fetchall()
        ObjID = pd.DataFrame(ObjID, columns=["ID", "Pkt"])

        # "OpenAdjustment"."VarianceComponent" (global test and s0²)
        query5 = 'SELECT "sigma2apost" FROM "OpenAdjustment"."VarianceComponent" WHERE "type" = 0'
        curs.execute(query5)
        globaltest = curs.fetchall()

        # shutdown and disconneted from the database
        curs.execute("SHUTDOWN")
        curs.close()
        conn.close()
        print("Successfully read new alignment data")

        ## return results
        return PktApost, PktID, ObjApost, ObjID, globaltest

    except Exception as e:
        print(f"Problem with reading the database. {e}")
        return


# WriteDatabase
def WriteDatabase(queries, databasePath, enginePath):
    # Write the new measurments of control epoch into JAG3D-database
    try:
        # conntect to JAG3D-database
        conn = ConnectDatabase(databasePath, enginePath)
        curs = conn.cursor()
        for i in range(len(queries)):
            curs.execute(queries[i])  # send queries to database

        # shutdown and disconneted from the database
        curs.execute("SHUTDOWN")
        curs.close()
        conn.close()
        print("Database update successfull!")

    except Exception as e:
        print(f"Problem with reading the database: {e}")
        return


# Check Observation groups
# In order to be able to perform an unique query, these are Observation groups required
# Read these from the JAG3D database
def CheckGroups(databasePath, enginePath):
    # conntect to JAG3D-database
    conn = ConnectDatabase(databasePath, enginePath)
    curs = conn.cursor()
    curs.execute(
        'SELECT * FROM "OpenAdjustment"."ObservationGroup"'
    )  # Get the group ids
    obsGroups = curs.fetchall()
    obsGroups = pd.DataFrame(
        obsGroups, columns=["id", "name", "type", "enable", "ref", "order"]
    )

    # shutdown and disconneted from the database
    curs.execute("SHUTDOWN")
    curs.close()
    conn.close()

    # Filter the observation groups of the Control epoch and sort them by there type (L,Hd,...)
    obsGroups_lists = (
        obsGroups[obsGroups["ref"] == False].groupby("type")["id"].apply(list)
    )
    # collect the data in DataFrame
    obsGroups_id_c = obsGroups_lists.reset_index(
        name="id_list"
    )  

    return obsGroups_id_c

# Write queries to update the measurement
def createQueries(
    groups_type_nr, filePathDatumPoints, filePathObjectPoints, controlEpoch_df
):
    ## Read obersavtion from control epoch
    obs = controlEpoch_df

    ## Read start data
    datumPoints = pd.read_csv(
        filePathDatumPoints,
        delimiter="\t",
        header=None,
        skipinitialspace=True,
    )

    datumPoints = datumPoints.iloc[:, 0].astype(str).str.strip() # get id of data points

    objectPoints = pd.read_csv(
        filePathObjectPoints,
        delimiter="\t",
        header=None,
        skipinitialspace=True,
    )
    objectPoints = objectPoints.iloc[:, 0].astype(str).str.strip()  # get id of object points

    ## Write Database queries
    queries = []  # List of SQL-queries

    # Rename object points in observation-file (only measurements from control epoch) "nr_c"
    object_points_list = objectPoints.tolist()
    append_suffix_if_in_list = lambda value: (
        f"{value}_c" if str(value) in object_points_list else str(value)
    )  
    # append _c
    obs["StID"] = obs["StID"].apply(append_suffix_if_in_list)
    obs["TarID"] = obs["TarID"].apply(append_suffix_if_in_list)
    obs["Val"].astype(float)

    # deactivate missing points (not measured in this epoch)
    extended_object_points = (objectPoints.astype(str).str.rstrip() + "_c").tolist()
    allPoints = (
        np.concatenate([datumPoints, extended_object_points]).astype(str).tolist()
    )
    missing = [
        element for element in allPoints if element not in obs[["StID", "TarID"]].values
    ]
    for element in missing:
        query = f'UPDATE "OpenAdjustment"."PointApriori" SET "enable" = FALSE WHERE "name" = \'{element}\''
        queries.append(query)

    ## Update data from control epoch - points that where not measured are deactivated
    """
    type    Observation
    1   	Leveling data
    2       Direction sets
    3       Horizontal distances
    4       Slope distances
    5       Zenith angles
    """
    groups_type_map = {"L": 1, "Hz": 2, "Hd": 3, "Sd": 4, "V": 5}

    # Create queries to update database
    for i in range(obs.shape[0]):
        jj = obs.loc[i, "group_id_txt"]
        g_nr = groups_type_map.get(jj)
        groups_type_nr["type"] = groups_type_nr["type"].astype(int)
        g_id = (
            ",".join(
                map(
                    str,
                    groups_type_nr.loc[
                        groups_type_nr["type"] == g_nr, "id_list"
                    ].values[0],
                )
            )
            .replace("[", "")
            .replace("]", "")
            .replace(",", "")
            .replace(" ", ",")
        )
        # if value is an angle --> to rad
        if g_nr in {2, 5}:
            valueNew = obs.loc[i, "Val"] / RHO
        else:
            valueNew = obs.loc[i, "Val"]

        # Build SQL-query
        query = f"""UPDATE "OpenAdjustment"."ObservationApriori"
                    SET "value_0" = {valueNew}
                    WHERE "group_id" IN ({g_id})
                    AND "start_point_name" = '{obs.loc[i, "StID"]}'
                    AND "end_point_name" = '{obs.loc[i, "TarID"]}';"""
        queries.append(query)
    return queries
