import os, sys
from pathlib import Path
import matplotlib.pyplot as plt 

# 1. import the Experiment object from LAMP 
from LAMP import Experiment

ROOT_FOLDER = str(Path.cwd().parent.parent) #Path.cwd().parent.parent#Path(__file__).resolve().parents[1] # absolute path to the experiment config files and other subfolders; 2 directories up in this case (assuming script in in ./scripts/eSpec/script.py)
sys.path.append(ROOT_FOLDER)
# import diagnostics.ESpec_
ex = Experiment(ROOT_FOLDER)



