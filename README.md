# Fireball III Analysis Github

This repository contains analysis scripts for the Fireball III experiment. This repository requires the pypi module LAMP to run. Please see "SWAN ONLY setup pyenv with LAMP in SWAN - do this every time you re-start SWAN" for instructions on how to set up a custom Python environment on SWAN and install dependencies, including LAMP.

## Table of Contents
- [Installation](#nstallation)
    - [Setting up the Fireball Github](#Set-up-Fireball-Githu)
    - [SWAN ONLY setup python environment with LAMP in SWAN - do this every time you re-start SWAN](SWAN-ONLY-setup-python-environment-with-LAMP-in-SWAN---do-this-every-time-you-re-start-SWAN)
    - [Installation on a local machine](#Installation-on-local-machine)
- [Overview](#Overview)
    - [Fireball III analysis github structure](#Fireball-_III-_analysis-github-structure) 
    - [Adding New Diagnostics](#adding-new-diagnostics)
- [References](#References)

## Installation

### Setting up the Fireball Github 

Clone the repository:


```bash
git clone https://github.com/ELos385/Fireball_III_analysis.git
```

Copy _local.toml and rename it local.toml.

### Dependencies

scipy

skimage

pandas

toml

opencv

LAMP 

    pypi: https://pypi.org/project/lamp/
    
    GitHub: https://github.com/brendankettle/LAMP\\


### SWAN ONLY setup pyenv with LAMP in SWAN - do this every time you re-start SWAN

Only do this if you are using SWAN. 


Open ```setup_pyenv.sh``` in ```Fireball_III_analysis```. Set ```ENV_NAME``` to name your environment (e.g. ```"FBIII"```):

```bash
ENV_NAME="FBIII"
```

save the file.

Open a terminal and navigate to the ```Fireball_III_analysis``` directory (should be under SWAN_projects). In the terminal, run:

```bash
chmod +x setup_pyenv.sh
./setup_pyenv.sh
```

When running a jupyter notebook which requires LAMP, select the kernel ```"Python <env_name>"``` from the drop down menu.  

### Installation on a local machine

If you are running on a local machine (not SWAN), I recommend creating a new python environment and installing the python libraries listed under "dependencies".
    
You will also need to change the PATH in local.toml to point to the location your data is saved in locally.
    

### Fireball_III analysis github structure

The ```Fireball_III_analysis``` github is structured as outlined in the LAMP documentation, please read this before writing anything or running any scripts.

### Adding New Diagnostics

See the LAMP documentation for guidance.

My example initialisations for Fireball III - specific diagnostics (HRM5 & HRM6) are in diagnostics.toml.

To add a new diagnostic, ```<NewDiag>```:
Add a new header to diagnostics.toml, follow the existing structure shown in my example and in the LAMP documentation.

Create a Python file in the diagnostics/ folder with a class for your diagnostic. Copy from
existing Fireball III diagnostic classes and modify as needed.

Store analysis scripts (these can also be copied from Fireball 3 analysis) in ```scripts/<NewDiag>/```

Store the diagnosti calibration files under ```./calibs/```

## References

SWAN Custom Kernels: https://swan-community.web.cern.ch/t/installing-custom-jupyter-kernels-at-swan-startup/297

LAMP PyPI: https://pypi.org/project/lamp/

LAMP GitHub: https://github.com/brendankettle/LAMP

Fireball III Analysis Repository: https://github.com/ELos385/Fireball_III_analysis
