#!/bin/bash
# -----------------------------------------------
# setup_local.sh
# 
# Usage: 
# chmod +x setup_local.sh
# ./setup_local.sh
# This script sets up a Python environment
# -----------------------------------------------
python3 -m venv FBIII
source FBIII/bin/activate
pip install -r Requirements.txt
python3 -m ipykernel install --user --name FBIII --display-name "FBIII"

cp FireballIII.py ./FBIII/lib/python3.12/site-packages/LAMP/DAQs