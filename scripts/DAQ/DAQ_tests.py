import sys
from pathlib import Path
import logging
from LAMP import Experiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_FOLDER = str(Path.cwd()) #Path.cwd().parent.parent#Path(__file__).resolve().parents[1] # absolute path to the experiment config files and other subfolders; 2 directories up in this case (assuming script in in ./scripts/eSpec/script.py)
sys.path.append(ROOT_FOLDER)

ex = Experiment(ROOT_FOLDER)

print("Experiment configuration:")
for key, value in ex.config.items():
    if isinstance(value, dict):
        logger.debug(f"{key}:")
        for subkey, subvalue in value.items():
            logger.debug(f"  {subkey}: {subvalue}")
    else:
        logger.debug(f"{key}: {value}")

template = ex.get_diagnostic('Template')

logger.debug("Diagnostics configuration:")
for key, value in template.config.items():
    if isinstance(value, dict):
        logger.debug(f"{key}:")
        for subkey, subvalue in value.items():
            logger.debug(f"  {subkey}: {subvalue}")
    else:
        logger.debug(f"{key}: {value}")



# shot_dict_string_exists = 'test.asc'
# shot_dict_string_nonexists = 'nonexistent.asc'
# shot_dict_filename_single = {'filename': 'test.asc'}
# shot_dict_filename_multiple = {'filename': ['test.asc', 'test2.asc']}
shot_dict_timestamp_single_short = {'timestamp': '20260212'}
# shot_dict_timestamp_single_long = {'timestamp': ['20260212235959']}
# shot_dict_timestamp_multiple = {'timestamp': ['20260212','20260218']}
# shot_dict_timestamp_wrong_format = {'timestamp': ['202adhajs hdj0212','202asdasdhj60218']}
# shot_dict_timeframe_working = {'timeframe': ['20260212','20260218']}
shot_data = template.get_shot_data(shot_dict_timestamp_single_short)

print("Shot data content:")
print(shot_data)