import pandas as pd
import numpy as np
from lib.jag3dBatchLib import *


RHO = 200 / np.pi

def createQueries(
    groups_type_nr, filePathDatumPoints, filePathObjectPoints, controlEpoch_df
):
    obs = controlEpoch_df
    ## Read start data
    datumPoints = pd.read_csv(
        filePathDatumPoints,
        delimiter="\t",
        header=None,
        skipinitialspace=True,
    )
    #datumPoints.reset_index(drop=True, inplace=True)
    datumPoints = datumPoints.iloc[:, 0].astype(str).str.strip() # get id of data points
    print(datumPoints)

    objectPoints = pd.read_csv(
        filePathObjectPoints,
        delimiter="\t",
        header=None,
        skipinitialspace=True,
    )
    objectPoints = objectPoints.iloc[:, 0].astype(str).str.strip()  # get id of object points
    print(objectPoints)

    ## Write Database queries
    queries = []  # List of SQL-queries

    # Rename object points in observation-file (only measurements from control epoch)
    object_points_list = objectPoints.tolist()
    append_suffix_if_in_list = lambda value: (
        f"{value}_c" if str(value) in object_points_list else str(value)
    )  # append _c
    obs["StID"] = obs["StID"].apply(append_suffix_if_in_list)
    obs["TarID"] = obs["TarID"].apply(append_suffix_if_in_list)
    obs["Val"].astype(float)

    # deactivate missing points (not measured this epoch)
    # print(objectPoints)
    extended_object_points = (objectPoints.astype(str).str.rstrip() + "_c").tolist()
    # print(datumPoints)
    allPoints = (
        np.concatenate([datumPoints, extended_object_points]).astype(str).tolist()
    )
    # print(obs[["StID", "TarID"]].values)
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
        # new values from new observation
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
        #print(queries)
    return queries