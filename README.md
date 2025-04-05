# Leica Total Station Control via Raspberry Pi (GeoCOM)
JAG3D-Batch Raspi-TS extends the functionality of the base JAG3D-Batch Project by integrating the Leica GeoCOM interface, thereby allowing completely automated capturing of observations via a Leica Total Station and a Raspberry Pi.

## Requirements

- **Licensed GeoCOM interface** on the total station
- **Leica Total Station**, e.g., TS15 with Leica Viva field software
- **Raspberry Pi** with Linux (e.g., Raspberry Pi OS)
- **Connection cables**: GEV189 or GEV267 (USB to 5-pin, RS232)
- **Python 3** and required libraries
- Configuration file: `config_tachy.ini`


## Setup

### 1. Activate GeoCOM Interface on the Total Station

1. Start the total station and access the main menu.
2. Navigate to:  
   `Main Menu → Instrument 3 → Connections → Additional Connections`
3. Enable **GeoCOM** and set the connection to **Cable**.
4. Open the "Device..." menu and select **RS232**.
5. Reset all settings to default using `F5 (Standard)`, and save with `F1 (Save)`.

**Note:** After this, make sure to perform stationing and set the correct prism type.


### 2. Connect to the Raspberry Pi

1. Connect the USB end of the cable to the Raspberry Pi.
2. Connect the 5-pin end to the total station.
3. Check the assigned device path on the Raspberry Pi using:

   ```bash
   dmesg | grep tty
   ```

   Note the `/dev/ttyUSBX` path.


### 3. Configure the Python Measurement Program

1. Edit the `config_tachy.ini` file.

#### Example Configuration:

```ini
[Serial]
baudRate = 115200
port = /dev/ttyUSB0

[ATM]
# Atmospheric parameters, optional sensor integration

[Output]
# Directory for measurement results

[Input]
# Path to the target point list
```

2. Adjust the baud rate and port according to your total station and Raspberry Pi.


## Usage

After successful setup, you can start the Python program to perform a automated measurement.

```bash
python3 your_measurement_program.py
```
