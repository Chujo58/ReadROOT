**Created by :** Chloé Legué

**Current version date :** 2022/12/02

**Version =** 2.2.6

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

This code was made for the coincidence experiment at McGill University. The code allows the user to choose a folder containing the results saved from the CoMPASS software made by CAEN. This code should be used with the CAEN DT5751 or with any other digitizer that uses CoMPASS to save files. This code is also capable of reproducing most of the graphics made by the CoMPASS Plot:

* Energy Histogram
* PSD Histogram
* Time Histogram
* TOF Histogram
* MCS Graph

Other graphs are not available at the moment. Do note that the log mode is not working at the moment and will be fixed at a later date.

**Update Log**

- Added GUI 2.0 (Recolor and rework of the first version)
- Changed the icons for the CoMPASS tabs.
- Added the remaining 2D histograms. Need to be coded.

Please refer to the Wiki to know how to use GUI properly.
