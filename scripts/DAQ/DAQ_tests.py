import sys
from pathlib import Path
import logging
from LAMP import Experiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_FOLDER = str(Path.cwd()) #Path.cwd().parent.parent#Path(__file__).resolve().parents[1] # absolute path to the experiment config files and other subfolders; 2 directories up in this case (assuming script in in ./scripts/eSpec/script.py)
sys.path.append(ROOT_FOLDER)

ex = Experiment(ROOT_FOLDER)
diag_config = ex.diags['SCOPE1'].config

logger.debug("Experiment configuration:")
for key, value in ex.config.items():
    if isinstance(value, dict):
        logger.debug(f"{key}:")
        for subkey, subvalue in value.items():
            logger.debug(f"  {subkey}: {subvalue}")
    else:
        logger.debug(f"{key}: {value}")

template = ex.get_diagnostic('ORCA')

logger.debug("Diagnostics configuration:")
for key, value in template.config.items():
    if isinstance(value, dict):
        logger.debug(f"{key}:")
        for subkey, subvalue in value.items():
            logger.debug(f"  {subkey}: {subvalue}")
    else:
        logger.debug(f"{key}: {value}")

# Test get_shot_data with filename input
shot_data = ex.DAQ.get_shot_data('ORCA', {'filename': 'test35104283.3726821.dac'})
logger.info(f"Shot data keys: {shot_data.keys()}")
logger.info(f"Shot data: {shot_data}")

# Test get_shot_data with filename input
shot_data = ex.DAQ.get_shot_data('ORCA', "test35104283.3726821.dac")
logger.info(f"Shot data keys: {shot_data.keys()}")
logger.info(f"Shot data: {shot_data}")



# # Test get_shot_data with filename input
# shot_data = ex.DAQ.get_shot_data('SCOPE1', {'timestamp': '20250602182450'})
# logger.info(f"Shot data keys: {shot_data.keys()}")
# logger.info(f"Shot data: {shot_data}")

# # Test get_shot_data with string input
# shot_data = ex.DAQ.get_shot_data('SCOPE1', 'scope1__ALL_20250602182440870.csv')
# logger.info(f"Shot data keys: {shot_data.keys()}")
# logger.info(f"Shot data: {shot_data}")

