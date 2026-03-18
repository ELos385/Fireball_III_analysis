#!/bin/bash
set -euo pipefail

ENV_NAME="FBIV"
PYTHON_VERSION="3.12"
MAMBA_ROOT_PREFIX="${HOME}/mamba"
MICROMAMBA="${MAMBA_ROOT_PREFIX}/bin/micromamba"
ENV_PATH="${MAMBA_ROOT_PREFIX}/envs/${ENV_NAME}"

unset PYTHONHOME
unset PYTHONPATH
unset LD_LIBRARY_PATH
unalias python 2>/dev/null || true

if [ ! -f "${MICROMAMBA}" ]; then
    mkdir -p "$(dirname "${MICROMAMBA}")"
    cd "${MAMBA_ROOT_PREFIX}"
    wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
fi

eval "$(${MICROMAMBA} shell hook --shell=bash)"

if [ ! -x "${ENV_PATH}/bin/python" ]; then
    ${MICROMAMBA} create -y -p "${ENV_PATH}" \
        python=${PYTHON_VERSION} ipykernel scipy matplotlib pandas scikit-image opencv toml ipywidgets ipympl
fi

${MICROMAMBA} run -p "${ENV_PATH}" python -c "import ipykernel"

if ! ${MICROMAMBA} run -p "${ENV_PATH}" python -c "import LAMP" >/dev/null 2>&1; then
    ${MICROMAMBA} run -p "${ENV_PATH}" python -m pip install --upgrade pip
    ${MICROMAMBA} run -p "${ENV_PATH}" python -m pip install LAMP==0.1.0.post1
fi

${MICROMAMBA} run -p "${ENV_PATH}" python -m ipykernel install \
  --prefix "/home/${USER}/.local" \
  --name "${ENV_NAME}" \
  --display-name "Python (${ENV_NAME})"

echo "Setup complete."
