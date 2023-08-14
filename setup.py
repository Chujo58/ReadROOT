__version__ = "2.4.3"

from setuptools import setup

description = open("READme.md").read()

setup(
    name = "ReadROOT",
    version = __version__,
    description = "Easy GUI made to read ROOT files created by the CoMPASS software distribued by CAEN.",
    long_description = description,
    long_description_content_type = "text/markdown",
    author = "Chloé Legué",
    author_email= "chloe.legue@mail.mcgill.ca",
    project_urls = {
        "Repository" : "https://github.com/Chujo58/ReadROOT",
        "Documentation" : "https://github.com/Chujo58/ReadROOT/wiki"
    },
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
            "./config.json",
            "./discord.mp3"
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
        "cppimport",
        "mpl_scatter_density",
        "rich",
        "pyautogui",
        "playsound==1.2.2"
    ],
    include_package_data= True,
    python_requires = ">=3.11"
)