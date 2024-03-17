**Created by :** Chloe Legue

**Current version date :** 2024/03/17

<p align=center>
<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.10-green.svg"></a>
<a target="_blank" href="https://pypi.org/project/ReadROOT/" title="PyPI version"><img src="https://img.shields.io/pypi/v/ReadROOT?logo=pypi"></a>
</p>

ReadROOT is an easy GUI made to read ROOT files created by the CoMPASS software distributed by CAEN. This GUI will also allow the user to plot the different graphs from the CoMPASS software.

# How to install ReadROOT

The ReadROOT package is currently on PyPi. This means it can be installed via a `pip` install.

## Create a virtual environment with Anaconda

Using Anaconda, creating a virtual environment is an easy task:

```
conda create --name new_env python==3.11.3
```

This line above will create a `Python` environment with the 3.11.3 update of `Python`. Some extra instructions need to be followed in the Anaconda terminal before the virtual environment is finalized. This is the version that was used to create this package, so it is better to use it.

## Activating and downloading the package

Once the virtual environment is created, it can be easily activated using `conda activate new_env`. From this point on, Anaconda will consider you are using the `new_env` environment which runs `Python` 3.11.3.

To download the ReadROOT package, the following command can be sent:

```
pip install ReadROOT
```

This will install the latest version of ReadROOT posted on PyPi. After all dependencies are installed, ReadROOT will be installed in your environment. To know more about the GUI and other functionalities of ReadROOT, you can navigate in this Wiki to find more information.

## Modifying some files

> This is no longer necessary if the newer `Merger` is used. The old C++ code was made for the previous Root Reader version.

In order for the time of flight (TOF) functions to work, C++ was used (Python was too slow). C++ needs very specific header files and the complete path to those files is needed. The two files that have those headers are `wrap.cpp` and `funcs.hpp`. If an error shows up when ReadROOT is imported (something along the lines of C++ not being able to find a header file) then verify those two.
