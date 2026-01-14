## Table of contents
- [Set up virtual environment in SWAN which supports LAMP](#Set-up-virtual-environment-in-SWAN-which-supports-LAMP)
    - [1: Clear SWAN Environment Variables](#1:-clear-swan-environment-variables)
    - [2: Install Micromamba (Lightweight Conda Replacement) if it doesn't exist](#2:-Install-Micromamba-(Lightweight-Conda-Replacement)-if-it-doesn't-exist)
    - [3: Set up the Micromamba environment](#3:-Set-up-the-Micromamba-environment)
    - [4: Make Micromamba persistent in SWAN](#4:-Make-Micromamba-persistent-in-SWAN)
    - [5: Create a Custom Python Environment](#5:-Create-a-Custom-Python-Environment)
    - [6: activate micromamba environment](#6:-activate-micromamba-environment)
    - [7: Install LAMP in the environment](#7:-Install-LAMP-in-the-environment)
    - [8: Configure Jupyter Kernel](#8:-Configure-Jupyter-Kernel)
    - [9: Write bash script to automatically load settings](#9:-Write-bash-script-to-automatically-load-settings)
    - [10: Run bash script to automatically load settings when you start SWAN (do this at the start of every session](#10:-Run-bash-script-to-automatically-load-settings-when-you-start-SWAN-(do-this-at-the-start-of-every-session)

# Set up virtual environment in SWAN which supports LAMP - Only do this ONCE when setting up LAMP in SWAN

Start SWAN session, open terminal

## 1: Clear SWAN Environment Variables

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

## 2: Install Micromamba (Lightweight Conda Replacement) if it doesn't exist

```markdown
```bash
if [ ! -f "${MICROMAMBA}" ]; then
    mkdir -p $(dirname ${MICROMAMBA})
    cd ${MAMBA_ROOT_PREFIX}
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
      | tar -xvj bin/micromamba
fi
```

## 3: Set up the Micromamba environment

```markdown
```bash
export MAMBA_ROOT_PREFIX=${HOME}/mamba
MICROMAMBA=${MAMBA_ROOT_PREFIX}/bin/micromamba
```

## 4: Make Micromamba persistent in SWAN

    replace <cernusername> with your CERN username

```markdown
```bash
micromamba shell init --shell bash --root-prefix=/eos/home-i03/e/<cernusername>/mamba
source ~/.bashrc
```

## 5: Create a Custom micromamba Environment

    Create a new environment named <env_name> (replace <env_name> with the name of your environment)

```markdown
```bash
$MICROMAMBA create -p <env_name> python=3.12 ipykernel scipy matplotlib pandas scikit-image opencv toml
```

## 6: Activate micromamba environment

```markdown
```bash
micromamba activate <env_name>
```

## 7: Install LAMP in the environment

```markdown
```bash
pip install LAMP
```

## 8: Configure Jupyter Kernel

    Create the SWAN kernel directory

```markdown
```bash
mkdir -p /home/<cernusername>/.ipython/kernels/<env_name>
```
    Find the Python path:
    
```markdown
```bash
micromamba run -n <env_name> which python
```
    Example output:

```markdown
```bash
/eos/home-i03/e/<cernusername>/mamba/envs/<env_name>/bin/python
```

    Create kernel.json:

```markdown
```bash
nano /home/<cernusername>/.ipython/kernels/<env_name>/kernel.json
```

    inside in the file, paste:

```markdown
```bash
{
  "argv": [
    "/eos/home-i03/e/<cernusername>/mamba/envs/<env_name>/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],
  "display_name": "Python <env_name>",
  "language": "python"
}
```

    Save with: Ctrl + O, Enter, Ctrl + X.

    Install the kernel so Jupyter recognizes it:
```markdown
```bash
micromamba run -n FBIII python -m ipykernel install \
  --prefix /home/<cernusername>/.local \
  --name FBIII \
  --display-name "Python <env_name>"
```

    when running a jupyter notebook which requires LAMP, select the kernel "Python <env_name>" from the drop down menu


## Write bash script to automatically load settings in SWAN (only do this once)

open setup_swan_kernel.sh in Fireball_III_analysis
set the following variables (replace <env_name> with the name of your environment, replace <cernusername> with your CERN username)
    
ENV_NAME=<env_name>
CERN_USER=<cernusername>
    
## Run bash script to automatically load settings when you start SWAN (do this at the start of every session)
    
open a terminal and run:
    
```markdown
```bash
    chmod +x setup_swan_kernel.sh
    ./setup_swan_kernel.sh
```

    
