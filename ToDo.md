To Code:
* [ ] Maybe add a function to calibrate the x scale (ADC bins to eV).
* [ ] In the `__init__.py`, add a function to choose the header files' location (for the C++ part). If the headers are not the good ones, C++ won't find them and we need the full path for it to work. Make it so that a selection (tkinter maybe) shows up to choose the files we want. 
* [X] Add buttons to choose the TOF channels.

PLOTS TO DO

* [X] ENERGY
* [X] PSD
* [X] TIME
* [ ] TOF - cpp
* [ ] PSD vs ENERGY
* [ ] ENERGY VS ENERGY
* [ ] TOF VS ENERGY
* [X] MCS

## C++ TOF
Note that for the C++ TOF, we might want to save some of the data in order to reuse it for the Energy vs Energy and TOF vs Energy plot. What can and could be done, is to save said data within the `FILTERED` folder or we can make a new folder called `C++ TOF` and save the data in there. Then before we recalculate anything we verify that the folder exists.