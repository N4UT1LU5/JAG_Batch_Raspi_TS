# JAG3D-Batch

- JAG3D-Batch is an extension for the adjustment software [JAG3D](https://software.applied-geodesy.org/en/) that facilitates automatic deformation analyses. This tool is useful for users who require an automated open source workflow instructions for geodetic applications.
The following is a step-by-step guide. Firstly, the installation and then the workflow with this Python module is described. 
---

## Features
- Automated JAG3D deformation analysis for two epochs.
- can be fully automated with additional open source software

---

## Installation
Only for Windows (this version is for windows but can be adapted for other platforms running JAG3D)

### Prerequisites
1. **Download and unpack JAG3D:**  
   - Get the latest release: [JAG3D Releases](https://github.com/applied-geodesy/jag3d/releases)  
   - Extract the package and copy all files and folders to your JAG-Batch directory
2. **Install Python:**  
   - Download and install Python: [Python Downloads](https://www.python.org/downloads/)
   - Restart your PC after installation

### Virtual Environment Setup (is recommended - not mandatory)
1. Navigate to your project directory (e.g., `C:\Users\user\Downloads\JAG3D_Batch`) in Terminal
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:

   ```cmd
   .venv\Scripts\activate
   ```
   *(Refer to the [Python documentation](https://docs.python.org/3/library/venv.html) for more details on virtual environments.)*
4. Install dependencies (all libraries that are required):
   ```bash
   pip install -r requirements.txt
   ```

---

## Workflow

### Step 1: Create JAG3D Project
Follow the project structure from the `JAG3D_Batch_example` project in `/jag3d_project`

#### Data Preparation
1. **Datum Points**
   - Export raw datum points as `data/start/datumPoints_apriori.txt` and replace the example data
2. **Object Points**
   - naming convention for Control epoch: `Nr_c`.
   - Export reference epoch (without `_c`) as `data/start/objectPoints_ref_apriori.txt` and replace the example data

### Step 2: Observation Configuration
1. Import the observation of the first two epochs into JAG3D (normal procedure).
2. Enable *congruence analysis* in `properties/leastsquares`
3. Rename all object points of the control epoch (`Nr_c`) using search and replace
4. Perform a least-squares adjustment - check for mistakes
5. Save the configuration in the `jag3d_project` folder.

**For help:** Refer to the [JAG3D Tutorial on Congruence Analysis](https://software.applied-geodesy.org/wiki/tutorial/congruenceanalysis)

### Step 3: Configure `config_jag.ini`
Adapt the `config_jag.ini` file to your monitoring project requirements

### Step 4: Run the automated Analysis
1. Replace the `data/controlEpoch/obs_c.txt` file with the new observation
2. Execute the main script:
   ```bash
   python main.py
   ```
3. Results will be displayed in the console:

   | **Parameter**             | **Description**                                |
   |---------------------------|------------------------------------------------|
   | Point number              | Unique identifier for each analyzed point    |
   | Deformation vector (`dx`, `dy`, `dz`) | Changes in x, y, z directions for each point |
   | Apriori test statistic (`T_prio`) | Statistic to evaluate deformation significance |
   | Statistical test result (`Sig`) | Whether deformation is statistically significant |
   | Point type                | Identifies as either a datum or object point |

### Automation
- Automate the last steps using tools like [Node-RED](https://nodered.org/).
- This allows for a fully automatic monitoring workflow.
- Update the `data/controlEpoch/obs_c.txt` file in the first step and in the second step execute `main.py`
---

## Handling Datum Changes
1. Apply the necessary changes in JAG3D as usual.
2. Replace the updated files in the `data/start` folder.
3. Restart the normal workflow
