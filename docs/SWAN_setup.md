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

# Set up virtual environment in SWAN which supports LAMP - Only do this ONCE, to use LAMP

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

```markdown
```bash
micromamba shell init --shell bash --root-prefix=/eos/home-i03/e/elos/mamba
source ~/.bashrc
```

## 5: Create a Custom micromamba Environment

Create a new environment named <env_name>:

```markdown
```bash
$MICROMAMBA create -p <env_name> python=3.12 ipykernel scipy matplotlib pandas scikit-image opencv toml
```

## 6: activate micromamba environment

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
    Example output:

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

when running a jupyter notebook which requires LAMP, select the kernel "Python (FBIII)" from the drop down menu

## Write bash script to automatically load settings
