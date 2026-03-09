#!/bin/bash
set -euo pipefail

# -----------------------------------------------
# setup_pyenv.sh
#
# Usage: ./setup_pyenv.sh
# Sets up a micromamba-based Python environment
# for the Fireball DAQ and registers a Jupyter kernel.
# -----------------------------------------------

# -----------------------------
# Configuration
# -----------------------------
ENV_NAME="FBIII"                 # Name of your custom environment
PYTHON_VERSION="3.12"            # Python version for environment
MAMBA_ROOT_PREFIX="${HOME}/mamba"
MICROMAMBA="${MAMBA_ROOT_PREFIX}/bin/micromamba"
ENV_PATH="${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}"
# KERNEL_DIR="${HOME}/.ipython/kernels/${ENV_NAME}"

# -----------------------------
# 1: Clear SWAN Environment Variables
# -----------------------------
unset PYTHONHOME
unset PYTHONPATH
unset LD_LIBRARY_PATH
unalias python &>/dev/null || true

echo "Cleared conflicting environment variables."

# -----------------------------
# 2: Install micromamba if missing
# -----------------------------
if [ ! -f "${MICROMAMBA}" ]; then
    echo "Installing micromamba..."
    mkdir -p "${MAMBA_ROOT_PREFIX}"
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest \
      | tar -xvj -C "${MAMBA_ROOT_PREFIX}" bin/micromamba
else
    echo "Micromamba already exists."
fi

echo "Micromamba path: ${MICROMAMBA}"
echo "Environment path: ${ENV_PATH}"

# -----------------------------
# 3: Make micromamba persistent
# -----------------------------
# eval "$(${MICROMAMBA} shell hook --shell=bash)"
# echo "Micromamba initialized."

# -----------------------------
# 4: Create custom environment if missing
# -----------------------------
if [ ! -d "${ENV_PATH}" ]; then
    echo "Creating environment ${ENV_NAME}..."
    "${MICROMAMBA}" create -y -p "${ENV_PATH}" -c conda-forge \
        python="${PYTHON_VERSION}" pip \
        ipykernel scipy matplotlib pandas scikit-image opencv toml ipywidgets ipympl
else
    echo "Environment ${ENV_NAME} already exists."
fi

# -----------------------------
# 5: Activate environment
# -----------------------------
# echo "Activating environment ${ENV_NAME}..."
# eval "$(${MICROMAMBA} shell hook --shell=bash)"
# micromamba activate "${ENV_NAME}"

# -----------------------------
# 6: Check installed modules, install any pre-requisites if missing.
# -----------------------------
# List modules by their Python import names

# MODULES=(ipywidgets ipympl)

# missing=()

# # Check each module
# for mod in "${MODULES[@]}"; do
#   if ! ${MICROMAMBA} run -p "${ENV_PATH}" python -c "import ${mod}" >/dev/null 2>&1; then
#     echo "${mod} missing"
#     missing+=("${mod}")
#   else
#     echo "${mod} already installed"
#   fi
# done

# # Install missing modules (if any)
# if [ ${#missing[@]} -gt 0 ]; then
#   echo "Installing: ${missing[*]}"
#   ${MICROMAMBA} install -y -p "${ENV_PATH}" "${missing[@]}"
# else
#   echo "All modules already installed"
# fi

# -----------------------------
# 7: Install LAMP if missing
# -----------------------------
echo "Checking if LAMP is installed..."
if ! "${MICROMAMBA}" run -p "${ENV_PATH}" python -c "import LAMP" >/dev/null 2>&1; then
    echo "LAMP not found. Installing with pip..."
    "${MICROMAMBA}" run -p "${ENV_PATH}" python -m pip install LAMP
else
    echo "LAMP is already installed."
fi

# -----------------------------
# 8: Configure Jupyter kernel
# -----------------------------
# echo "Setting up Jupyter kernel..."
# mkdir -p "${KERNEL_DIR}"

# PYTHON_PATH=$(micromamba run -n "${ENV_NAME}" which python)
# KERNEL_JSON="${KERNEL_DIR}/kernel.json"

# cat > "${KERNEL_JSON}" <<EOL
# {
#   "argv": [
#     "${PYTHON_PATH}",
#     "-m",
#     "ipykernel_launcher",
#     "-f",
#     "{connection_file}"
#   ],
#   "display_name": "Python (${ENV_NAME})",
#   "language": "python"
# }
# EOL

# Register kernel so Jupyter can see it
echo "Registering Jupyter kernel..."

export JUPYTER_DATA_DIR="${HOME}/.local/share/jupyter"
unset JUPYTER_PATH
unset JUPYTER_CONFIG_DIR
mkdir -p "${JUPYTER_DATA_DIR}/kernels"

"${MICROMAMBA}" run -p "${ENV_PATH}" env \
    JUPYTER_DATA_DIR="${JUPYTER_DATA_DIR}" \
    python -m ipykernel install \
    --user \
    --name "${ENV_NAME}" \
    --display-name "Python (${ENV_NAME})"

PYTHON_PATH=$("${MICROMAMBA}" run -p "${ENV_PATH}" python -c "import sys; print(sys.executable)")
echo "Python executable: ${PYTHON_PATH}"
echo "Setup complete."