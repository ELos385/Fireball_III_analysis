#!/bin/bash
set -euo pipefail

# Set environment variables for setup
ENV_NAME="Fireball_env"
PYTHON_VERSION="3.12"
MAMBA_ROOT_PREFIX="${HOME}/mamba"
MICROMAMBA="${MAMBA_ROOT_PREFIX}/bin/micromamba"
# ENV_PATH="/eos/project/h/hiradmat/HRMT Experiments/2026/HRMT76 - FIREBALL-IV/envs/${ENV_NAME}"
ENV_PATH="${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}"

LOGFILE="${HOME}/setup_${ENV_NAME}_$(date +%Y%m%d_%H%M%S).log"

# -----------------------------
# Logging setup
# -----------------------------
exec > >(tee -a "${LOGFILE}") 2>&1

log() {
    echo "[$(date '+%F %T')] $*"
}

section() {
    echo ""
    echo "=================================================="
    log "$*"
    echo "=================================================="
}

# -----------------------------
# Helper functions
# -----------------------------

has_module() {
    local mod="$1"
    "${MICROMAMBA}" run -p "${ENV_PATH}" python -c "import ${mod}" >/dev/null 2>&1
}

ensure_mamba_modules() {
    local missing=()
    while [ "$#" -gt 0 ]; do
        local import_name="$1"
        local package_name="$2"
        shift 2

        if has_module "${import_name}"; then
            echo "OK: ${import_name}"
        else
            echo "Missing: ${import_name} -> ${package_name}"
            missing+=("${package_name}")
        fi
    done

    if [ "${#missing[@]}" -gt 0 ]; then
        echo "Installing with micromamba: ${missing[*]}"
        "${MICROMAMBA}" install -y -p "${ENV_PATH}" "${missing[@]}"
    else
        echo "All micromamba-managed modules already installed."
    fi
}

ensure_pip_module() {
    local import_name="$1"
    local pip_spec="$2"

    if has_module "${import_name}"; then
        echo "OK: ${import_name}"
    else
        echo "Missing: ${import_name} -> ${pip_spec}"
        "${MICROMAMBA}" run -p "${ENV_PATH}" python -m pip install "${pip_spec}"
    fi
}

section "Fireball IV python environment setup script"
log "Run by ${USER}"

# Unset SWAN paths that could interfere with setup
section "Cleaning SWAN environment"

unset PYTHONHOME
unset PYTHONPATH
unset LD_LIBRARY_PATH
unalias python 2>/dev/null || true

# Download micromamba if needed
section "Checking micromamba"

if [ ! -f "${MICROMAMBA}" ]; then
    log "Installing micromamba..."
    mkdir -p "$(dirname "${MICROMAMBA}")"
    cd "${MAMBA_ROOT_PREFIX}"
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
else
    log "Micomamba already installed."
fi

# Create the FBIV environment in mamba
section "Checking environment ${ENV_NAME}"

if [ ! -x "${ENV_PATH}/bin/python" ]; then
    log "Creating environment at ${ENV_PATH}..."
    ${MICROMAMBA} create -y -p "${ENV_PATH}" "python=${PYTHON_VERSION}"
else
    log "Environment already exists."
fi

section "Checking micromamba packages"

ensure_mamba_modules \
    ipykernel ipykernel \
    scipy scipy \
    matplotlib matplotlib \
    pandas pandas \
    skimage scikit-image \
    cv2 opencv \
    toml toml \
    ipywidgets ipywidgets \
    ipympl ipympl

section "Ensuring pip"
"${MICROMAMBA}" run -p "${ENV_PATH}" python -m pip install --upgrade pip >/dev/null

section "Installing LAMP 1.0.1.post1"
ensure_pip_module LAMP "LAMP==0.1.0.post1"

section "pip dependency check"

"${MICROMAMBA}" run -p "${ENV_PATH}" python -m pip check || log "WARNING: dependency issues detected"

section "Registering Jupyter kernel"
${MICROMAMBA} run -p "${ENV_PATH}" python -m ipykernel install \
  --prefix "/home/${USER}/.local" \
  --name "${ENV_NAME}" \
  --display-name "Python (${ENV_NAME})"

section "Setup complete"
log "Log file saved to: ${LOGFILE}"
