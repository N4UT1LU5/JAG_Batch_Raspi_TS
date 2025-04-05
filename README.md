
# Leica Total Station Control via Raspberry Pi (GeoCOM) + JAG3D Integration

This project extends the [JAG3D-Batch](https://github.com/) project by providing a lightweight, Python-based interface for controlling Leica total stations via a Raspberry Pi using the GeoCOM protocol. It enables automated measurements, atmospheric data integration, and batch processing of deformation analysis in JAG3D.

## Folder Structure

```
project_root/
├── config_tachy.ini           # Config for total station settings
├── config_jag.ini             # Config for JAG3D project interaction
├── data/
│   ├── punktliste/            # List of target points
│   ├── measurements/          # Raw measurements
│   ├── controlEpoch/          # Converted measurements for JAG3D
│   └── start/                 # Exported coordinates from JAG3D
├── jag3d_project/             # Preconfigured JAG3D project
├── hypersql/                  # HyperSQL DB for JAG3D
├── lib/                       # Python scripts
├── venv/                      # Python virtual environment
└── main.py                    # Entry point for measurement & analysis
```

## Setup

### 1. Total Station Preparation (GeoCOM)

1. Start the total station and access the main menu.
2. Navigate to:  
   `Main Menu → Instrument 3 → Connections → Additional Connections`
3. Enable **GeoCOM** and set the connection to **Cable**.
4. Open the "Device..." menu and select **RS232**.
5. Reset all settings to default using `F5 (Standard)`, and save with `F1 (Save)`.

### 2. Raspberry Pi Connection

Connect via GEV189 or GEV267 cable. Check the serial port:

```bash
dmesg | grep tty
```

Use the assigned `/dev/ttyUSBX` in your config file.

### 3. Python Configuration

Edit `config_tachy.ini`:

```ini
[Serial]
baudRate = 115200
port = /dev/ttyUSB0

[Misc]
# additional totalstation measurement settings

[ATM]
# Optional atmospheric sensor config

[Output]
# Path for measurements

[Input]
# Path to point list
```

## Measurement & Deformation Analysis

1. Perform initial setup and record a point list consisting of angles and distances. These measurements tell the total station where to find the targets.
2. Save the point list under `data/punktliste/` (same format as the sample).
3. Import coordinates to JAG3D as datum and new points.

### JAG3D Preparation

- Prepare the `jag3d_project/` according to the deformation monitoring workflow described in the base JAG3D-Batch project.
- Export reference epoch coordinates (datum & object points) via right-click in JAG3D > "Export raw data".
- Place those files in `data/start/`.
- Match filenames in `config_jag.ini` under `[Start]`.

### Java Runtime

Ensure you have Java 21 installed. The script uses Java for JAG3D batch processing.
Donwload the used version from [Bellsoft](https://download.bell-sw.com/java/21.0.5+11/bellsoft-jre21.0.5+11-linux-aarch64-full.deb)

```bash
sudo apt install ./bellsoft-jre21.0.5+11-linux-aarch64-full.deb
```

## Running the Script

Once the project is setup, you can run the main script to start measurements and analysis.:

```bash
python3 main.py
```

The script:
- Triggers a new measurement
- Converts results for JAG3D
- Updates project DB with new control epoch
- Executes batch-based congruence analysis
- Logs results in a file

## Automating with Cron

To run every hour open the crontab editor:

```bash
crontab -e
```

Add:

```bash
0 * * * * cd /home/pi/project/ && /home/pi/project/venv/bin/python3 /home/pi/project/main.py
```

> [!NOTE]
> the paths must be adjusted to your project path.
