#!/bin/bash
set -euo pipefail

# Set environment variables for setup
ENV_NAME="fireball_env"
SHARED_PATH="/eos/project/h/hiradmat/HRMT Experiments/2026/HRMT76 - FIREBALL-IV/temp"
PYTHON_VERSION="3.12"
MAMBA_ROOT_PREFIX="${SHARED_PATH}/mamba"
MICROMAMBA="${MAMBA_ROOT_PREFIX}/bin/micromamba"
# ENV_PATH="/eos/project/h/hiradmat/HRMT Experiments/2026/HRMT76 - FIREBALL-IV/envs/${ENV_NAME}"
ENV_PATH="${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}"

LOGFILE="${HOME}/setup_${ENV_NAME}_$(date +%Y%m%d_%H%M%S).log"

# -----------------------------
# Logging setup
# -----------------------------
if [ ! -d "$SHARED_PATH" ]; then
    echo "Error: Directory does not exist: $SHARED_PATH" >&2
    exit 1
fi
echo "Directory ready: ${SHARED_PATH}"

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

section "Fireball IV hared environment kernel registration"
log "Run by ${USER}"

# Unset SWAN paths that could interfere with setup
section "Cleaning SWAN environment"

unset PYTHONHOME
unset PYTHONPATH
unset LD_LIBRARY_PATH
unalias python 2>/dev/null || true

"${MICROMAMBA}" run -p "${ENV_PATH}" python -m pip check || log "WARNING: dependency issues detected"

section "Registering Jupyter kernel"
"${MICROMAMBA}" run -p "${ENV_PATH}" python -m ipykernel install \
  --prefix "/home/${USER}/.local" \
  --name "${ENV_NAME}" \
  --display-name "Python (${ENV_NAME})"

section "Setup complete"
log "Log file saved to: ${LOGFILE}"
