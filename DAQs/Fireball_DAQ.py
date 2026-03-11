import os
from pathlib import Path
import re
import numpy as np
from LAMP.DAQ import DAQ
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

class Fireball_DAQ(DAQ):
    """Interface layer for Fireball experimental series
    """
    __version__ = 0.1
    __name__ = 'Fireball_DAQ'
    __authors__ = ['Brendan Kettle', 'Eva Los', 'Maximilian Mudra', 'Margarida Pereira']

    # These file_types can be used so far
    supported_file_types = ['pickle', 'json', 'csv', 'numpy', 'npy', 'toml', 'tif', 'asc', 'scope']

    def __init__(self, exp_obj):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        super().__init__(exp_obj)
        level_str = self.ex.config.get('logging', {}).get('level', 'INFO')

        if not isinstance(level_str, str):
            raise TypeError(f"Logging level must be a string, got {type(level_str)}")

        level = getattr(logging, level_str.upper(), None)
        if level is None:
            raise ValueError(f"Invalid logging level in config: {level_str}")

        logging.getLogger().setLevel(level)
        logger.info(f"Logging level set to {level_str.upper()}")
        return


    def load_asc(self, filepath):
        """Loads data from .asc files, which are used for spectroscopy in the Fireball
        series. These files are essentially .csv files, but without header row and
        meta data stored at the end.

        Parameters
        ----------
            filepath : str
                The path to the .asc file where the spectroscopy data is stored.

        Returns
        -------
            data : np.ndarray
                The spectroscopy data as a numpy array after being loaded from the .asc file.
        """

        if not Path(filepath).suffix == '.asc':
            raise ValueError(f"Error: load_asc() function only supports .asc files, "
                            f"but {filepath} has extension {Path(filepath).suffix}")
        data = np.loadtxt(filepath, delimiter=',', dtype=float, max_rows=1024, usecols=range(1025))
        
        if isinstance(data[0], np.void): # if problems loading datatypes, try to return an array
            data = np.array(list(map(list, data)))
        return data

    def load_scope(self, filepath):
        """
            Loads data from .csv scope files, which are used for Bdot diagnostic. 
            Skips first 16 rows.

            Parameters
            ----------
                filepath : str
                    The path to the .asc file where the spectroscopy data is stored.

            Returns
            -------
            dict
                {
                    "time": np.ndarray,
                    "channels": np.ndarray,
                    "channel_names": list of str,
                    "N": int,      # number of samples
                    "dt": float    # time step
                }
        """
        logger.debug(f"Loading scope data from {filepath} in {self.__name__} DAQ.")

        if not Path(filepath).suffix == '.csv':
            raise ValueError(f"Error: load_scope() function only supports .csv files, "
                            f"but {filepath} has extension {Path(filepath).suffix}")
            
        # Read all lines
        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Extract N and dt from header
        N = None
        dt = None
        
        for line in lines:
            # Strip whitespace and split by comma
            parts = line.strip().split(',')
            if parts[0].lower() == "sample interval":
                dt = float(parts[1])
            if parts[0].lower() == "record length":
                N = int(parts[1])
            # Stop early if we have both
            if N is not None and dt is not None:
                break

        if N is None or dt is None:
            raise ValueError("Could not find Sample Interval or Record Length in header.")

        # If file has no samples, return None immediately
        if N == 0:
            return None


        # Find label line (contains 'Labels')
        label_index = None
        for i, line in enumerate(lines):
            if "Labels" in line:
                label_index = i
                break
    
        if label_index is None:
            raise ValueError("Could not find Labels in scope CSV.")
    
        # Extract channel names
        label = lines[label_index].strip().split(',')
        label_names = label[1:]  # everything after Labels
        
        # Find header line (contains 'TIME')
        header_index = None
        for i, line in enumerate(lines):
            if "TIME" in line:
                header_index = i
                break
    
        if header_index is None:
            raise ValueError("Could not find Time header in scope CSV.")
    
        # Extract channel names
        header = lines[header_index].strip().split(',')
        channel_names = header[1:]  # everything after time
    
        # Load numeric data only
        data = np.genfromtxt(
            filepath,
            delimiter=',',
            skip_header=header_index + 1
        )

        # If somehow data is empty, return None
        if data.size == 0:
            return None
        
        time = data[:, 0]
        channels = data[:, 1:]

        # --- Optional alternative: compute N and dt from time array ---
        # N = len(time)
        # dt = np.mean(np.diff(time))  # robust even if slightly nonuniform
    
        return {
            "time": time,
            "channels": channels,
            "channel_names": channel_names,
            "label_names": label_names,
            "N": N,
            "dt": dt
               
        }
    
    
    # Overwrite DAQ load_data to handle custom data types, e.g. asc files from spectroscopy
    def load_data(self, shot_filepath, file_type):
        """Loads data from a given filepath, with support for custom file types such as .asc files used for spectroscopy in the Fireball series.
        For supported file types, it calls the parent DAQ load_data function, and for .asc files, it uses the custom load_asc function. For scope
        .csv files, it uses the custom load_scope function. For image files, it uses the parent DAQ load_imdata function.

        Parameters
        ----------
            shot_filepath : str
                The path to the file where the data is stored.
            file_type : str
                The type of the file, which determines how the data will be loaded.

        Returns
        -------
            data : np.ndarray
                The data loaded from the file, in a format determined by the file type.
        """
        logger.debug(f"Loading data from {shot_filepath} with file_type {file_type} in {self.__name__} DAQ.")
        if file_type in ['pickle', 'json', 'csv', 'numpy', 'npy', 'toml', 'tif']:
             data = super().load_data(shot_filepath, file_type=file_type)
        elif file_type == 'asc':
            data = self.load_asc(Path(shot_filepath))
        elif file_type == 'scope':
            data = self.load_scope(shot_filepath)
        elif file_type == 'image':
            data = super().load_imdata(shot_filepath)
        else:
            raise ValueError(f"Error: file_type {file_type} not supported in Fireball DAQ.")

        return data


    def get_shot_data(self, diag_name, shot_dict):
        """Provides shot_data depending on the data_type or data_ext of the diagnostic.
        For images, uses load_csv_image() to load the data, and for other data types, 
        uses load_data().

        Parameters
        ----------
            diag_name : str
                The name of the diagnostic for which we want to get the shot data. This is
                used to look up the appropriate data_type and data_ext in the diagnostic's
                config.
            shot_dict : dict or str
                A dictionary containing information about the shots, which can be used to
                construct the appropriate file paths. Alternatively, this can be a string
                containing a raw file path to the data.
        
        Returns
        -------
            dict with keys 'filename' and 'data'
            'filename' : list
                A list of the filenames corresponding to the shot data that was loaded.
            'data' : list
                A list of shot data for each shot corresponding to the shot_dict.
        """
        logger.debug(f"Getting shot data for diagnostic {diag_name} with shot_dict {shot_dict} in Fireball DAQ.")
        diag_config = self.ex.diags[diag_name].config
        
        data_type = diag_config['data_type']
        if data_type not in self.supported_file_types:
            raise ValueError(f"Error: data_type '{data_type}' not supported in Fireball DAQ.")
        
        diag_data_path = os.path.join(Path(self.data_folder),
                                      Path(diag_config['data_folder'].lstrip("/\\")))
        
        # Check if shot_dict is dictionary
        if isinstance(shot_dict, dict):
            # Supported shot_dict keys: filename, timestamp, timeframe            
            required = ['filename', 'timestamp']
            # required = ['filename', 'timestamp', 'timeframe']
            if not any(key in shot_dict for key in required):
                raise ValueError(f"Error: shot_dict {shot_dict} is not a valid input for "
                                 f"get_shot_data() in Fireball DAQ. Please provide "
                                 f"either a dictionary with keys 'filenames', 'timestamp',"
                                 f"'timeframe' or a raw filepath string.")

            if 'filename' in shot_dict:
                logger.debug(f"shot_dict contains filename: {shot_dict['filename']}")
                in_file = shot_dict['filename']
                # if isinstance(in_files, str):
                #     in_files = [in_files]
                if not isinstance(in_file, str):
                    raise TypeError("Filenames must be provided as a string")

                # for file in in_files:
                shot_filepath = os.path.join(diag_data_path,
                                                       Path(in_file.lstrip("/\\")))
                logger.debug(f"Constructed filepath from filename: {shot_filepath}")
            
            elif 'timestamp' in shot_dict:
                logger.debug(f"shot_dict contains timestamp: {shot_dict['timestamp']}")
                in_timestamp = shot_dict['timestamp']
                if not isinstance(in_timestamp, str):
                    raise TypeError("Timestamps must be provided as a string")

                shot_filepath = self.timestamp_to_filename(in_timestamp,diag_data_path)[0]
                logger.debug(f"Constructed filepath from timestamp: {shot_filepath}")
            


        # A single (relative) filepath can be provided as a string
        elif isinstance(shot_dict, str):
            logger.debug(f"shot_dict is a string, treating as filepath: {shot_dict}")
            logger.debug(f"diag_data_path: {diag_data_path}")
            base = Path(diag_data_path).resolve()
            path = (base / shot_dict).resolve()
            logger.debug(f"Resolved path: {path}")

            if base not in path.parents and path != base:
                raise ValueError("Path escapes base directory")
            shot_filepath = path
        else:
            raise ValueError(f"Error: shot_dict {shot_dict} is not a valid input for "
                             f"get_shot_data() in Fireball DAQ. Please provide either "
                             f"a dictionary with keys 'filenames', 'timestamp', "
                             f"or a raw filepath string.")

        # Convert to Path objects for easier handling
        shot_filepath = Path(shot_filepath)        

        # Filter files according to prefix and extension !!!
        # if 'data_stem' in diag_config:
        #     stem = diag_config['data_stem']
        #     shot_filepaths = [
        #         f for f in shot_filepaths
        #         if f.name.startswith(stem)
        #     ]
        # if 'data_ext' in diag_config:
        #     ext = diag_config['data_ext']
        #     shot_filepaths = [
        #         f for f in shot_filepaths
        #         if f.suffix == ext
        #     ]

        if os.path.exists(shot_filepath):
            shot_data = self.load_data(shot_filepath, data_type)
        else:
            raise ValueError(f"Error: No data could be loaded for {diag_name} with "
                             f"shot_dict {shot_dict} in Fireball DAQ. Please "
                             f"check the provided shot_dict and ensure that the "
                             f"corresponding files exist and are in the correct format.")

        return shot_data

    def timeframe_to_filenames(self, diag_name, timestamp_begin, timestamp_end):        
        """Function to convert a timeframe to a list of corresponding filenames in the diagnostic's data_dir.
        The timeframe should be provided as a two string timestamps in the format 
        YYYYMMDDHHMMSS or YYYYMMDD. The function will search the diagnostic's data directory for files whose
        names contain timestamps between the two values and return a list of file paths for those files whose
        timestamps fall within the specified timeframe.

        Parameters
        ----------
            diag_name : str
                The name of the diagnostic for which we want to get the filenames corresponding to the specified timeframe
            time_stamp_begin : str
                The start timestamp of the timeframe, in the format YYYYMMDDHHMMSS or YYYYMMDD
            time_stamp_end : str
                The end timestamp of the timeframe, in the format YYYYMMDDHHMMSS or YYYYMMDD

        Returns
        -------
            file_names : list
                A list of file names that have timestamps in their filenames falling within the specified timeframe.
        """
        logger.debug(f"Getting filenames for diagnostic {diag_name} with timeframe ({timestamp_begin}, {timestamp_end}) in Fireball DAQ.")
        diag_config = self.ex.diags[diag_name].config
        diag_data_path = Path(self.data_folder) / diag_config["data_folder"].lstrip("/\\")

        file_names =  []

        if not isinstance(timestamp_begin, str) or not isinstance(timestamp_end, str):
            raise TypeError("Timeframe values must be strings")

        # Normalize timestamps to ensure they are in the same format
        start_time = self.normalize_timestamp(timestamp_begin,'DOWN')
        end_time = self.normalize_timestamp(timestamp_end,'UP')

        pattern = r"^\d{14}$"  # YYYYMMDDHHMMSS (14 digits)

        if not re.fullmatch(pattern, start_time):
            raise ValueError(f"Invalid start_time format: {start_time}")

        if not re.fullmatch(pattern, end_time):
            raise ValueError(f"Invalid end_time format: {end_time}")

        if start_time > end_time:
            raise ValueError("start_time must be <= end_time")

        logger.debug(f"Looking for files with timestamps between {start_time} and {end_time} in {diag_data_path}")
        
        timestamp_pattern = re.compile(r"\d{14}")

        for file in diag_data_path.iterdir():
            if not file.is_file():
                continue

            match = timestamp_pattern.search(file.name)
            if not match:
                continue

            file_timestamp = match.group(0)

            if start_time <= file_timestamp <= end_time:
                file_names.append(file.name)

        file_names.sort()
        

        if not file_names:
            logger.warning(
                f"No files found with timestamps between "
                f"{start_time} and {end_time} in {diag_data_path}"
            )
        logger.debug(f"Found {len(file_names)} files with timestamps between "
                     f"{start_time} and {end_time} in {diag_data_path}: {file_names}")


        return file_names

    def timestamp_to_filename(self, timestamp, data_path):
        """Function to convert a timestamp to a list of corresponding filenames in the
        diagnostic's data_dir
        """
        file_paths = []
        
        for file in os.listdir(data_path):
            if timestamp in file:
                file_paths.append(os.path.join(data_path, file))
        if len(file_paths) == 0:
            logger.warning(f"timestamp_to_filename: No files found with timestamp {timestamp} in {data_path}")

        if len(file_paths) > 1:
            logger.warning(f"timestamp_to_filename: Multiple files found with timestamp {timestamp} in {data_path}: {file_paths}")
        elif len(file_paths) == 0:
            raise ValueError(f"timestamp_to_filename: No files found with timestamp {timestamp} in {data_path}")

        return file_paths
    
    def normalize_timestamp(self, timestamp, direction):
        """Converts timestamps of the form YYYYMMDD to YYYYMMDD000000 or YYYYMMDD235959,
        depending on direction, for timeframe searching. If timestamp is already in the
        form YYYYMMDDHHMMSS, it is returned unchanged.

        Parameters
        ----------
            timestamp : str
                The timestamp to normalize, in the form YYYYMMDD or YYYYMMDDHHMMSS
            direction : str
                The direction to normalize the timestamp, either 'UP' or 'DOWN'. 'UP'
                will normalize to the end of the day (YYYYMMDD235959), while 'DOWN' will
                normalize to the start of the day (YYYYMMDD000000).
        Returns
        -------
            normalized_timestamp : str
                The normalized timestamp in the form YYYYMMDDHHMMSS
        """
        if len(timestamp) == 8:
            if direction == 'UP':
                return timestamp + "235959"   # end of day
            elif direction == 'DOWN':
                return timestamp + "000000"   # start of day
        return timestamp
