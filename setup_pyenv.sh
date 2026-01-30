#!/bin/bash
# -----------------------------------------------
# setup_swan_lamp.sh
#
# Usage: ./setup_swan_lamp.sh
# -----------------------------------------------

set -euo pipefail

# -----------------------------
# Configuration
# -----------------------------
ENV_NAME="FBIII"                 # Name of your custom environment
PYTHON_VERSION="3.12"            # Python version for environment

MAMBA_ROOT_PREFIX="${HOME}/mamba"
MICROMAMBA="${MAMBA_ROOT_PREFIX}/bin/micromamba"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX}"
export MICROMAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX}"

# Always locate files relative to this script (so first run works from any cwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_FIREBALL="${SCRIPT_DIR}/FireballIII.py"

# -----------------------------
# 1: Clear SWAN Environment Variables (current shell only)
# -----------------------------
unset PYTHONHOME || true
unset PYTHONPATH || true
unset LD_LIBRARY_PATH || true
unalias python &>/dev/null || true

echo "Cleared SWAN environment variables..."

# -----------------------------
# 2: Install micromamba if missing
# -----------------------------
if [ ! -f "${MICROMAMBA}" ]; then
    echo "Installing micromamba..."
    #mkdir -p "$(dirname "${MICROMAMBA}")"
    mkdir -p "${MAMBA_ROOT_PREFIX}"
    cd "${MAMBA_ROOT_PREFIX}"
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
      | tar -xvj bin/micromamba
else
    echo "Micromamba already exists."
fi

# -----------------------------
# 3: Initialize micromamba for this shell
# -----------------------------
eval "$(${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" shell hook --shell=bash)"
echo "Micromamba initialized."

# -----------------------------
# 4: Create custom environment if missing
# -----------------------------
if [ ! -d "${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}" ]; then
    echo "Creating environment ${ENV_NAME}..."
    ${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" create -y -n "${ENV_NAME}" \
        python="${PYTHON_VERSION}" ipykernel scipy matplotlib pandas scikit-image opencv toml
else
    echo "Environment ${ENV_NAME} already exists."
fi

# -----------------------------
# 5: Install LAMP if missing
# -----------------------------
echo "Checking if LAMP is installed..."
if ! ${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" run -n "${ENV_NAME}" python -c "import LAMP" &>/dev/null; then
    echo "LAMP not found. Installing..."
    ${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" run -n "${ENV_NAME}" python -m pip install --upgrade pip
    ${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" run -n "${ENV_NAME}" python -m pip install LAMP
else
    echo "LAMP is already installed."
fi

# -----------------------------
# 6: Configure Jupyter kernel (both kernelspec locations)
# -----------------------------
echo "Setting up Jupyter kernel..."

PYTHON_PATH=$(${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" run -n "${ENV_NAME}" which python)

# Register kernel so Jupyter can see it
${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" run -n "${ENV_NAME}" python -m ipykernel install \
  --prefix "/home/${USER}/.local" \
  --name "${ENV_NAME}" \
  --display-name "Python ${ENV_NAME}"

# -----------------------------
# 6b: Copy FireballIII.py into LAMP DAQs folder
# -----------------------------
echo "Checking if FireballIII.py exists in LAMP.DAQs folder..."

if [ ! -f "${SRC_FIREBALL}" ]; then
    echo "Error: ${SRC_FIREBALL} not found."
    echo "Put FireballIII.py in the same directory as this script (or update SRC_FIREBALL)."
    exit 1
fi

DAQ_PATH=$(${MICROMAMBA} -r "${MAMBA_ROOT_PREFIX}" run -n "${ENV_NAME}" python - <<'PY'
import os
import LAMP.DAQs as DAQs
print(os.path.abspath(DAQs.__path__[0]))
PY
)

# Keep the last non-empty line, trim whitespace
DAQ_PATH=$(echo "${DAQ_PATH}" | awk 'NF{line=$0} END{print line}' | tr -d '[:space:]')

if [ -z "${DAQ_PATH}" ] || [ ! -d "${DAQ_PATH}" ]; then
    echo "Error: LAMP.DAQs folder not found / DAQ_PATH invalid: '${DAQ_PATH}'" >&2
    exit 1
fi

if [ -f "${DAQ_PATH}/FireballIII.py" ]; then
    echo "FireballIII.py already exists in ${DAQ_PATH}, skipping copy."
else
    cp -- "${SRC_FIREBALL}" "${DAQ_PATH}/"
    echo "FireballIII.py successfully copied to ${DAQ_PATH}"
fi

echo "Setup complete! You can now select 'Python (${ENV_NAME})' in Jupyter."
