#!/bin/bash
# -----------------------------------------------
# setup_swan_lamp.sh
# 
# Usage: ./setup_swan_lamp.sh
# This script sets up a SWAN-ready Python environment
# with LAMP and registers a Jupyter kernel.
# -----------------------------------------------

# -----------------------------
# Configuration - CHANGE THESE
# -----------------------------
ENV_NAME="FBIII"                 # Name of your custom environment
CERN_USER="elos"                 # Your CERN username
PYTHON_VERSION="3.12"            # Python version for environment
MAMBA_ROOT_PREFIX="${HOME}/mamba"
MICROMAMBA="${MAMBA_ROOT_PREFIX}/bin/micromamba"
KERNEL_DIR="${HOME}/.ipython/kernels/${ENV_NAME}"

# -----------------------------
# 1: Clear SWAN Environment Variables
# -----------------------------
unset PYTHONHOME
unset PYTHONPATH
unset LD_LIBRARY_PATH
unalias python &>/dev/null || true

echo "Cleared SWAN environment variables..."

# -----------------------------
# 2: Install micromamba if missing
# -----------------------------
if [ ! -f "${MICROMAMBA}" ]; then
    echo "Installing micromamba..."
    mkdir -p "$(dirname "${MICROMAMBA}")"
    cd "${MAMBA_ROOT_PREFIX}" || exit 1
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
      | tar -xvj bin/micromamba
else
    echo "Micromamba already exists."
fi

# -----------------------------
# 3: Make micromamba persistent
# -----------------------------
eval "$(${MICROMAMBA} shell hook --shell=bash)"
echo "Micromamba initialized."

# -----------------------------
# 4: Create custom environment if missing
# -----------------------------
if [ ! -d "${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}" ]; then
    echo "Creating environment ${ENV_NAME}..."
    ${MICROMAMBA} create -y -p "${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}" \
        python=${PYTHON_VERSION} ipykernel scipy matplotlib pandas scikit-image opencv toml
else
    echo "Environment ${ENV_NAME} already exists."
fi

# -----------------------------
# 5: Activate environment
# -----------------------------
echo "Activating environment ${ENV_NAME}..."
eval "$(${MICROMAMBA} shell hook --shell=bash)"
micromamba activate "${ENV_NAME}"

# -----------------------------
# 6: Install LAMP if missing
# -----------------------------
echo "Checking if LAMP is installed..."
if ! micromamba run -n "${ENV_NAME}" python -c "import LAMP" &>/dev/null; then
    echo "LAMP not found. Installing..."
    micromamba run -n "${ENV_NAME}" pip install --upgrade pip
    micromamba run -n "${ENV_NAME}" pip install LAMP
else
    echo "LAMP is already installed."
fi

# -----------------------------
# 7: Configure Jupyter kernel
# -----------------------------
echo "Setting up Jupyter kernel..."
mkdir -p "${KERNEL_DIR}"

PYTHON_PATH=$(micromamba run -n "${ENV_NAME}" which python)
KERNEL_JSON="${KERNEL_DIR}/kernel.json"

cat > "${KERNEL_JSON}" <<EOL
{
  "argv": [
    "${PYTHON_PATH}",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],
  "display_name": "Python (${ENV_NAME})",
  "language": "python"
}
EOL

# Register kernel so Jupyter can see it
micromamba run -n ${ENV_NAME} python -m ipykernel install \
  --prefix /home/${CERN_USER}/.local \
  --name ${ENV_NAME} \
  --display-name "Python ${ENV_NAME}"
  
# -----------------------------
# 7b: Copy FireballIII.py into LAMP DAQs folder if not already there
# -----------------------------
# echo "Checking if FireballIII.py exists in LAMP.DAQs folder..."

# # Get DAQ_PATH, ignoring LAMP startup message
# DAQ_PATH=$(micromamba run -n "${ENV_NAME}" python - <<'PYTHON_EOF'
# import os
# import LAMP.DAQs as DAQs
# # Only print the first path
# print(os.path.abspath(DAQs.__path__[0]))
# PYTHON_EOF
# )

# # Take only the last line in case LAMP prints messages before
# DAQ_PATH=$(echo "$DAQ_PATH" | tail -n 1 | tr -d '[:space:]')

# # Check and copy FireballIII.py only if necessary
# if [ -d "${DAQ_PATH}" ]; then
#     if [ ! -f "${DAQ_PATH}/FireballIII.py" ]; then
#         cp FireballIII.py "${DAQ_PATH}/"
#         echo "FireballIII.py copied to ${DAQ_PATH}"
#     else
#         echo "FireballIII.py already exists in ${DAQ_PATH}, skipping copy."
#     fi
# else
#     echo "Error: LAMP.DAQs folder not found at ${DAQ_PATH}"
# fi

echo "Setup complete! You can now select 'Python (${ENV_NAME})' in Jupyter."
