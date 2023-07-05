__version__ = "2.2.2"

from setuptools import setup

setup(
    name = "ReadROOT",
    version = __version__,
    description = "Easy GUI made to read ROOT files created by the CoMPASS software distribued by CAEN.",
    long_description = "ReadROOT is an easy GUI made to read ROOT files created by the CoMPASS software distributed by CAEN. This GUI will also allow the user to plot the different graphs from the CoMPASS software.",
    author = "Chloé Legué",
    author_email= "chloe.legue@mail.mcgill.ca",
    url = "https://github.com/Chujo58/ReadROOT",
    packages= [
        "ReadROOT",
        "ReadROOT.merge"
    ],
    package_dir = {
        "ReadROOT" : ".",
        "ReadROOT.merge" : "./merge"
    },
    package_data = {
        '' : [
            "./Images/*",
            "./Images/Log/*",
            "./Images/CoMPASS/*",
            "./funcs.hpp",
            "./funcs.cpp",
            "./wrap.cpp",
            "./config.json"
        ]
    },
    install_requires = [
        "uproot",
        "bytechomp",
        "numpy",
        "spinmob",
        "pandas",
        "pyqtgraph==0.13.3",
        "darkdetect",
        "pyqt5",
        "scipy",
        "matplotlib",
        "superqt",
        "bs4",
        "tk",
        "pint",
        "colorama",
        "termcolor",
        "cppimport"
    ],
    include_package_data= True,
    python_requires = ">3.11"
)