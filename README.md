Fireball III Analysis Setup on SWAN

This repository contains analysis scripts for the Fireball III experiment. This guide explains how to set up a custom Python environment on SWAN and install dependencies, including LAMP, so that notebooks and analysis scripts run smoothly.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Dependencies](#Dependencies)
- [Set up virtual environment in SWAN which supports LAMP](#Set-up-virtual-environment-in-SWAN-which-supports-LAMP)
    - [1: Clear SWAN Environment Variables](#1:-clear-swan-environment-variables)
    - [2: Install Micromamba (Lightweight Conda Replacement) if it doesn't exist](#2:-Install-Micromamba-(Lightweight-Conda-Replacement)-if-it-doesn't-exist)
    - [3: Set up the Micromamba environment](#3:-Set-up-the-Micromamba-environment)
    - [4: Make Micromamba persistent in SWAN](#4:-Make-Micromamba-persistent-in-SWAN)
    - [5: Create a Custom Python Environment](#5:-Create-a-Custom-Python-Environment)
    - [6: activate micromamba environment](#6:-activate-micromamba-environment)
    - [7: Install LAMP in the environment](#7:-Install-LAMP-in-the-environment)
    - [8: Configure Jupyter Kernel](#8:-Configure-Jupyter-Kernel)
- [Adding New Diagnostics](#adding-new-diagnostics)
- [References](#references)

## Prerequisites

    SWAN account at CERN.

## Dependencies
    LAMP:  
        pypi: https://pypi.org/project/lamp/
        GitHub: https://github.com/brendankettle/LAMP
    scipy
    skimage
    pandas
    toml
    opencv

## Set up virtual environment in SWAN which supports LAMP

Start SWAN session, open terminal

### 1: Clear SWAN Environment Variables

Create a script in your home directory called setup_custom_kernel.sh:

```markdown
```bash
#!/bin/bash
# Clear interfering environment variables
unset PYTHONHOME
unset PYTHONPATH
unset LD_LIBRARY_PATH
unalias python &>/dev/null
```

This ensures that SWAN’s default Python environment does not interfere with your custom setup.

### 2: Install Micromamba (Lightweight Conda Replacement) if it doesn't exist

```markdown
```bash
if [ ! -f "${MICROMAMBA}" ]; then
    mkdir -p $(dirname ${MICROMAMBA})
    cd ${MAMBA_ROOT_PREFIX}
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
      | tar -xvj bin/micromamba
fi
```

### 3: Set up the Micromamba environment

```markdown
```bash
export MAMBA_ROOT_PREFIX=${HOME}/mamba
MICROMAMBA=${MAMBA_ROOT_PREFIX}/bin/micromamba
```

### 4: Make Micromamba persistent in SWAN

```markdown
```bash
micromamba shell init --shell bash --root-prefix=/eos/home-i03/e/elos/mamba
source ~/.bashrc
```

### 5: Create a Custom micromamba Environment

Create a new environment named <env_name>:

```markdown
```bash
$MICROMAMBA create -p <env_name> python=3.12 ipykernel scipy matplotlib pandas scikit-image opencv toml
```

### 6: activate micromamba environment

```markdown
```bash
micromamba activate <env_name>
```

### 7: Install LAMP in the environment

```markdown
```bash
pip install LAMP
```

### 8: Configure Jupyter Kernel

    Create the SWAN kernel directory:

```markdown
```bash
mkdir -p /home/elos/.ipython/kernels/FBIII
```
    Find the Python path:
    
```markdown
```bash
micromamba run -n FBIII which python
```
# Example output:

```markdown
```bash
/eos/home-i03/e/elos/mamba/envs/FBIII/bin/python
```

    Create kernel.json:

```markdown
```bash
nano /home/elos/.ipython/kernels/FBIII/kernel.json
```
inside in the file, paste:

```markdown
```bash
{
  "argv": [
    "/eos/home-i03/e/elos/mamba/envs/FBIII/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],
  "display_name": "Python (FBIII)",
  "language": "python"
}
```

Save with: Ctrl + O, Enter, Ctrl + X.

    Install the kernel so Jupyter recognizes it:
```markdown
```bash
micromamba run -n FBIII python -m ipykernel install \
  --prefix /home/elos/.local \
  --name FBIII \
  --display-name "Python (FBIII)"
```

## Set up Fireball Github in your SWAN account

Clone the repository into SWAN:

```markdown
```bash
git clone https://github.com/ELos385/Fireball_III_analysis.git
```

Next, copy _local.toml and rename it local.toml.

Find the DAQ module path by running the following in the terminal:

```markdown
```bash
python -c "import LAMP.DAQs as DAQs; print(DAQs.__path__)"
```

which outputs /PATH_to_DAQ/ in the terminal

Copy FireballIII.py into the DAQ folder:

```markdown
```bash
cp FireballIII.py /PATH_to_DAQ/
```

## Fireball_III_analysis github structure

The Fireball_III_analysis github is structured as outlined in the LAMP documentations, please read this first.

## Adding New Diagnostics

    See the LAMP documentation for guidance.

    My examples for Fireball III-specific diagnostics (HRM5 & HRM6) are in diagnostics.toml.

    To add a new diagnostic, <NewDiag>:

        Create a Python file in the diagnostics/ folder with a class for your diagnostic. Copy from
        existing Fireball III diagnostic classes and modify as needed.

        Store analysis scripts in scripts/<NewDiag>/

        Store calibration files under calibs

References

    SWAN Custom Kernels: https://swan-community.web.cern.ch/t/installing-custom-jupyter-kernels-at-swan-startup/297

    LAMP PyPI: https://pypi.org/project/lamp/

    LAMP GitHub: https://github.com/brendankettle/LAMP

    Fireball III Analysis Repository: https://github.com/ELos385/Fireball_III_analysis



ChatGPT can make mistakes. Check important info. See Cookie Preferences.
