# Load the libraries
from os import listdir, makedirs
from os.path import join, dirname
import csv
import time
from datetime import datetime
import sys

import lib.surveytools as st
import lib.GeoCom as gc
from lib.GeoComEnumeration import *

def measurePoint(totalstation:gc.TotalStation,point,atm:gc.AtmosphericCorrectionData,twoFace:bool):
    if twoFace:
        point[2] = (point[2] + 200) % 400
        point[3] = 400 - point[3]
    hz = st.Angle.from_gon(point[2])
    vz = st.Angle.from_gon(point[3])


    measurementTargets = st.MeasurementTarget(
        1, hz, vz, 5.0
    )  # create an observation

    # move the prism with ATR
    totalstation.set_telescope_position(
        measurementTargets.direction,
        measurementTargets.zenith,
        PositionMode.AUT_PRECISE,
        ATRMode.AUT_TARGET,
    )
    time_tuple = time.localtime()
    measure_time = time.strftime("%Y.%m.%d %H:%M:%S", time_tuple)

    # Perform measurement
    m = totalstation.measure(measurementTargets.target_number, atm, measure_time)
    return m


def StartTachyMeasurement(
    outputPath: str,
    pktListPath: list,
    turnOff: bool,
    twoFace: bool,
    hasHeader: bool,
    lamb: float,
    pres: float,
    temp: float,
    serialPort: int,
    baudRate: int,
):
    """
    starts totalstation measurement and returns filename and path of Output
    """
    pkts = []

    outputName = f"Messung_{datetime.now().replace(microsecond=0).isoformat()}.txt"
    outputPath = f"{outputPath}{outputName}"

    # print(listdir(pktListPath))
    with open(join(pktListPath, listdir(pktListPath)[0])) as f:
        reader = csv.reader(f, delimiter=",")
        if hasHeader == True:
            next(reader, None)
        for row in reader:
            pkts.append([row[0], row[1], float(row[2]), float(row[3])])

    # Set up connection parameters
    t = gc.TotalStation(
        serialPort, baudrate=baudRate
    )  # Set the correct COM port!!!!

    # Output instrument name and software version
    # Test if connection works
    try:
        t.wake_up()  # Check if instrument is on
        print(
            f"Instrument Name: {t.get_instrument_name()} SRNR: {t.get_instrument_number()}"
        )
    except Exception as e:
        print("Error occurred while connecting to the total station:", e)
        sys.exit(1)

    # Pass atmospheric parameters to the object
    atm = gc.AtmosphericCorrectionData(
        lamb,
        pres,
        temp,
        temp,
    )  # Carrier wavelength, air pressure, temp, temp

    pkt_measure_list_L1=[]
    # Move to targets from list, measure and write data to text file
    for pkt in pkts:
        m = measurePoint(t,pkt,atm, False)
        pkt_measure_list_L1.append(m)
        # Format values
        z_return = m.zenith.value_rad * st.RHO
        sd_return = m.slope_distances.real
        hz_return = m.direction.value_rad * st.RHO
        # Write measurement values to file
        if not twoFace:
            output_line = (
                f"{pkt[0]},{pkt[1]},{hz_return},{z_return},{sd_return},{m.measure_time}\n"
            )
            makedirs(dirname(outputPath), exist_ok=True)
            with open(outputPath, "a") as f:
                f.write(output_line)
                
    if twoFace:
        for pkt, pkt_L1 in zip(reversed(pkts), reversed(pkt_measure_list_L1)):
            print(pkt_L1)
            m = measurePoint(t,pkt,atm,twoFace)
            print(m)

            hz_return = (pkt_L1.direction.value_rad * st.RHO + ((m.direction.value_rad * st.RHO - 200) % 400)) / 2
            z_return = (pkt_L1.zenith.value_rad * st.RHO + (400 - m.zenith.value_rad * st.RHO)) / 2
            sd_return = (m.slope_distances.real + pkt_L1.slope_distances.real) / 2
            output_line = (
                f"{pkt[0]},{pkt[1]},{hz_return},{z_return},{sd_return},{m.measure_time}\n"
            )
            makedirs(dirname(outputPath), exist_ok=True)
            with open(outputPath, "a") as f:
                f.write(output_line)
    
    # Turn off the instrument after measurement
    if turnOff:
        t.turn_off()

    return outputPath