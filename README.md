Fireball III Analysis Setup on SWAN

This repository contains analysis scripts for the Fireball III experiment. This guide explains how to set up a custom Python environment on SWAN and install dependencies, including LAMP, so that notebooks and analysis scripts run smoothly.
Table of Contents

##  Prerequisites

## Step 1: Clear SWAN Environment Variables

## Step 2: Install Micromamba

    Step 3: Create a Custom Python Environment

    Step 4: Install LAMP

    Step 5: Configure Jupyter Kernel

    Step 6: Launch SWAN Jupyter Notebook

    Adding New Diagnostics

    References
## Prerequisites

    SWAN account at CERN.

## Dependencies
    LAMP:  https://github.com/brendankettle/LAMP/blob/main/docs/UserGuide.md
    scipy
    skimage
    pandas
    toml
    opencv


## Set up virtual environment in SWAN which supports LAMP

Step 1: Clear SWAN Environment Variables

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
Step 2: Install Micromamba (Lightweight Conda Replacement)

### Set up the Micromamba environment:

```markdown
```bash
export MAMBA_ROOT_PREFIX=${HOME}/mamba
MICROMAMBA=${MAMBA_ROOT_PREFIX}/bin/micromamba

# Download micromamba if it doesn't exist
if [ ! -f "${MICROMAMBA}" ]; then
    mkdir -p $(dirname ${MICROMAMBA})
    cd ${MAMBA_ROOT_PREFIX}
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
      | tar -xvj bin/micromamba
fi
```

### make Micromamba persistent in SWAN:

micromamba shell init --shell bash --root-prefix=/eos/home-i03/e/elos/mamba
source ~/.bashrc

### Create a Custom Python Environment

Create a SWAN-safe environment named FBIII:

$MICROMAMBA create -p $ENV_PREFIX python=3.12 ipykernel scipy matplotlib pandas scikit-image opencv toml

### activate micromamba environment

micromamba activate FBIII

Install LAMP in the environment:

micromamba activate FBIII
pip install LAMP

Notes:

    LAMP PyPI: https://pypi.org/project/lamp/

    LAMP GitHub: https://github.com/brendankettle/LAMP

Minimum working example:

    Copy _local.toml and rename it local.toml.

    Find the DAQ module path:

python -c "import LAMP.DAQs as DAQs; print(DAQs.__path__)"

    Copy FireballIII.py into the DAQ folder:

cp FireballIII.py /PATH_to_DAQ/

Step 5: Configure Jupyter Kernel

    Create the SWAN kernel directory:

mkdir -p /home/elos/.ipython/kernels/FBIII

    Find the Python path:

micromamba run -n FBIII which python
# Example output:
/eos/home-i03/e/elos/mamba/envs/FBIII/bin/python

    Create kernel.json:

nano /home/elos/.ipython/kernels/FBIII/kernel.json

Paste:

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

Save with: Ctrl + O, Enter, Ctrl + X.

    Install the kernel so Jupyter recognizes it:

micromamba run -n FBIII python -m ipykernel install \
  --prefix /home/elos/.local \
  --name FBIII \
  --display-name "Python (FBIII)"

Step 6: Launch SWAN Jupyter Notebook

    Clone the repository inside SWAN:

git clone https://github.com/ELos385/Fireball_III_analysis.git

    Start Jupyter Notebook from SWAN:

jupyter notebook

Select Python (FBIII) kernel to use your custom environment.
Adding New Diagnostics

    See the LAMP documentation
    for guidance.

    My examples for Fireball III-specific diagnostics (HRM5 & HRM6) are in diagnostics.toml.

    To add a new diagnostic:

        Create a Python file in the diagnostics/ folder with a class for your diagnostic.

        Copy from existing Fireball III classes and modify as needed.

        Store analysis scripts in scripts/diagname/.

References

    SWAN Custom Kernels: https://swan-community.web.cern.ch/t/installing-custom-jupyter-kernels-at-swan-startup/297

    LAMP PyPI: https://pypi.org/project/lamp/

    LAMP GitHub: https://github.com/brendankettle/LAMP

    Fireball III Analysis Repository: https://github.com/ELos385/Fireball_III_analysis



ChatGPT can make mistakes. Check important info. See Cookie Preferences.
