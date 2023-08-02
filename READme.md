**Created by :** Chloé Legué

**Current version date :** 2023/08/02

**Version =** 2.3.17

**install**

1. Create a virtual environment (replace *env_name* with the name of your choice)

   ```bash
   python3 -m venv env_name
   ```
2. Activate the environment

   ```bash
   source env_name/bin/activate
   ```
3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

**Install with conda or normal Python distribution**

The installation process is described in the wiki of this Github repository. You can also find more information about how to use the different functions of this package in the wiki. Here is the link to the [installation](https://github.com/Chujo58/ReadROOT/wiki).

**Use of this code**

This code was made for the coincidence experiment at McGill University. The code allows the user to choose a folder containing the results saved from the CoMPASS software made by CAEN. This code should be used with the CAEN DT5751 or with any other digitizer that uses CoMPASS to save files. This code can reproduce all the different plots and histograms that the CoMPASS software can. Do note that 2D histograms might take longer to render or may simply lag the GUI. If this does happen, the graphics can be manually replotted. If the TOF histograms (or graphs that need the TOF data) lag the GUI, there are also ways to run the analysis manually to avoid problems.

Please refer to the Wiki to know how to use GUI properly.
