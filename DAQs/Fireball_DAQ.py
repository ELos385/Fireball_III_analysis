import os
from pathlib import Path
import re
import numpy as np
from LAMP.DAQ import DAQ

class Fireball_DAQ(DAQ):
    """Interface layer for Fireball experimental series
    """
    __version = 0.1
    __name = 'Fireball_DAQ'
    __authors = ['Brendan Kettle', 'Eva Los', 'Maximilian Mudra']

    # These file_types can be used so far
    supported_file_types = ['pickle', 'json', 'csv', 'numpy', 'npy', 'toml', 'tif', 'asc']


    def __init__(self, exp_obj):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        super().__init__(exp_obj)
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
        print(data)
        if type(data[0]) == np.void: # if problems loading datatypes, try to return an array
            data = np.array(list(map(list, data)))
        return data


    # Overwrite DAQ load_data to handle custom data types, e.g. asc files from spectroscopy
    def load_data(self, shot_filepath, file_type=None):
        print(f"Loading data from {shot_filepath} with file_type {file_type} in {self.__name} DAQ.")
        if file_type in ['pickle', 'json', 'csv', 'numpy', 'npy', 'toml', 'tif']:
             data = super().load_data(shot_filepath, file_type=file_type)
        elif file_type == 'asc':
            data = self.load_asc(Path(shot_filepath))
        # elif file_type == 'image':
            # data = super().load_imdata(shot_filepath)
        else:
            raise ValueError(f"Error: file_type {file_type} not supported in {self.__name} DAQ.")

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
            shot_data : list
                A list of shot data for each shot in the shot_dict.
        """

        # MM: TODO: We should really return a dictionary with a list of identifiers for
        # the data and the data itself, e.g. {"data":shot_data, "filenames":shot_filepaths}
        # or something like that, so that we can keep track of which data corresponds to
        # which file, and also so that we can return any relevant metadata that we might want
        # to use in the diagnostics later on.
        
        diag_config = self.ex.diags[diag_name].config
        
        data_type = diag_config['data_type']
        if not (data_type in self.supported_file_types):
            raise ValueError(f"Error: data_type '{data_type}' not supported in {self.__name} "
                             f"DAQ.")
        
        diag_data_path = os.path.join(Path(self.data_folder),
                                      Path(diag_config['data_folder'].lstrip("/\\")))
        
        # for now, just return an array, but we could also return a dictionary with the
        # data and the coordinates for images, for example. Or just return the raw data
        # and let the diagnostic handle it?
        shot_data = []
        key = None

        # Intermediate array of all relevant (absolute) filepaths
        shot_filepaths = []

        # Check if shot_dict is dictionary
        if isinstance(shot_dict, dict):
            # Possible shot_dict keys: filename, timestamp, timeframe            
            required = ['filename', 'timestamp', 'timeframe']
            if not any(key in shot_dict for key in required):
                raise ValueError(f"Error: shot_dict {shot_dict} is not a valid input for "
                                 f"get_shot_data() in {self.__name} DAQ. Please provide "
                                 f"either a dictionary with keys 'filenames', 'timestamp',"
                                 f"'timeframe' or a raw filepath string.")

            if 'filename' in shot_dict:
                key = 'filename'
                in_files = shot_dict['filename']
                labels = in_files
                if isinstance(in_files, str):
                    in_files = [in_files]

                for file in in_files:
                    shot_filepaths.append(os.path.join(diag_data_path,
                                                       Path(file.lstrip("/\\"))))
            
            elif 'timestamp' in shot_dict:
                key = 'timestamp'
                in_timestamps = shot_dict['timestamp']
                labels = in_timestamps
                if isinstance(in_timestamps, str):
                    in_timestamps = [in_timestamps]

                for timestamp in in_timestamps:
                    if not isinstance(timestamp, str):
                        raise TypeError("Timestamps must be strings")

                    shot_filepaths.extend(self.timestamp_to_filename(timestamp,diag_data_path))

                # Remove duplicates, if there are multiple timestamps that correspond to the same file
                shot_filepaths = list(set(shot_filepaths))
            
            elif 'timeframe' in shot_dict:
                key = 'timestamp'
                # Attempt to find files with timestamps in name that fall within
                # provided timeframe

                if not isinstance(shot_dict['timeframe'], (list, tuple)) or len(shot_dict['timeframe']) != 2:
                    raise ValueError("'timeframe' must be a list/tuple of length 2")

                start_time, end_time = shot_dict['timeframe']
                if not isinstance(start_time, str) or not isinstance(end_time, str):
                    raise TypeError("Timeframe values must be strings")

                # Normalize timestamps to ensure they are in the same format
                start_time = self.normalize_timestamp(start_time,'DOWN')
                end_time = self.normalize_timestamp(end_time,'UP')

                pattern = r"^\d{14}$"  # YYYYMMDDHHMMSS (14 digits)

                if not re.fullmatch(pattern, start_time):
                    raise ValueError(f"Invalid start_time format: {start_time}")

                if not re.fullmatch(pattern, end_time):
                    raise ValueError(f"Invalid end_time format: {end_time}")

                if start_time > end_time:
                    raise ValueError("start_time must be <= end_time")

                print(f"Looking for files with timestamps between {start_time} and {end_time} in {diag_data_path}")

                shot_filepaths = self.timeframe_to_filenames((start_time, end_time), diag_data_path)


                
        # A single (relative) filepath can be provided as a string
        elif isinstance(shot_dict, str):
            key = 'filename'
            base = Path(diag_data_path).resolve()
            path = (base / shot_dict).resolve()

            if base not in path.parents and path != base:
                raise ValueError("Path escapes base directory")
            labels = [Path(shot_dict).name]
            shot_filepaths = [path]
        
        else:
            raise ValueError(f"Error: shot_dict {shot_dict} is not a valid input for "
                             f"get_shot_data() in {self.__name} DAQ. Please provide either "
                             f"a dictionary with keys 'filenames', 'timestamp', 'timeframe', "
                             f"or a raw filepath string.")

        # Convert to Path objects for easier handling
        shot_filepaths = [Path(f) for f in shot_filepaths]        

        # Filter files according to prefix and extension
        if 'data_stem' in diag_config:
            stem = diag_config['data_stem']
            shot_filepaths = [
                f for f in shot_filepaths
                if f.name.startswith(stem)
            ]
        if 'data_ext' in diag_config:
            ext = diag_config['data_ext']
            shot_filepaths = [
                f for f in shot_filepaths
                if f.suffix == ext
            ]

        # Iterate through the filepaths and load the data
        for shot_filepath in shot_filepaths:
            if os.path.exists(shot_filepath):
                print(data_type)
                print(shot_filepath)
                shot_data.append(self.load_data(shot_filepath, data_type))
            else:
                print(f"Error: Could not find file {shot_filepath} for {diag_name}")

        if len(shot_data) == 0:
            print(f"Warning: No shot data loaded for diagnostic {diag_name} with "
                  f"shot_dict {shot_dict}! Does the file exist?")
            return None
        
        return {'key': key, 'labels': labels, 'data': shot_data}
        # {'key': 'filename', 'labels': ['file1.ext', 'file2.ext'], 'data': [data1, data2]}


    def timestamp_to_filename(self, timestamp, data_path):
        """Function to convert a timestamp to a list of corresponding filenames in the
        diagnostic's data_dir
        """
        file_paths = []
        
        for file in os.listdir(data_path):
            if timestamp in file:
                file_paths.append(os.path.join(data_path, file))
        if len(file_paths) == 0:
            print(f"Warning: No files found with timestamp {timestamp} in {data_path}")

        return file_paths
    

    def timeframe_to_filenames(self, timeframe, data_path):
        """
        Convert timeframe (start_time, end_time) to list of filepaths
        whose filenames contain YYYYMMDDHHMMSS timestamps.
        """

        start_time, end_time = timeframe
        data_path = Path(data_path)

        timestamp_pattern = re.compile(r"\d{14}")

        file_paths = []

        for file in data_path.iterdir():
            if not file.is_file():
                continue

            match = timestamp_pattern.search(file.name)
            if not match:
                continue

            file_timestamp = match.group(0)

            if start_time <= file_timestamp <= end_time:
                file_paths.append(file)

        file_paths.sort()

        if not file_paths:
            print(
                f"Warning: No files found with timestamps between "
                f"{start_time} and {end_time} in {data_path}"
            )

        return file_paths


    def todo(self, item):
        print(f"TODO: {item} functionality not implemented yet in {self.__name} DAQ.")
    

    def normalize_timestamp(self, timestamp, direction):
        if len(timestamp) == 8:
            if direction == 'UP':
                return timestamp + "235959"   # end of day
            elif direction == 'DOWN':
                return timestamp + "000000"   # start of day
        return timestamp