import os, sys
from pathlib import Path
import csv
import re
import time
import numpy as np
from LAMP.DAQ import DAQ
from LAMP.utils.io import load_file

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
    
    def load_csv_image(self, path:str)->tuple[np.ndarray, list, list]:
        """Loads image object from .csv given by DigiCam. Due to the way that the DigiCams store image data,
        the first column and first row have to be removed, as these contain coordinate information about the
        pixels.

        Parameters
        ----------
            path : str
                The path to the raw .csv file where the DigiCam image is stored.

        Returns
        -------
            img : np.ndarray
                The image as a numpy array after being loaded from the .csv, and after having its first column and
                first row trimmed.
            x_pixels : np.ndarray
                The trimmed top row of the image data, which encodes the x coordinates in mm.
            y_pixels : np.ndarray
                The trimmed first column of the image data, which encodes the y coordinates in mm.
        """

        #Remove top row and first column, as this is coordinate data
        try:
            img = np.genfromtxt(path, delimiter=',')
            x_coords = img[0, 1:]
            y_coords = img[1:, 0]
            img = img[1:, 1:]

            return {"IMG":img, "X":x_coords, "Y":y_coords}

        except Exception as e:
            ValueError(f"Error: DIGICAM image generation from {path} failed. {e}")

    def load_asc(self, filepath): # cold_dtypes=float
        # Pandas might be better here? problems with mixed data types...
        data = np.loadtxt(filepath, delimiter=',', dtype=float, max_rows=1, usecols=range(1025))
        print(data)
        if type(data[0]) == np.void: # if problems loading datatypes, try to return an array
            data = np.array(list(map(list, data)))
        return data

    # Overwrite DAQ load_data to handle custom data types, e.g. csv images from DigiCam
    def load_data(self, shot_filepath, file_type=None):
        print(f"Loading data from {shot_filepath} with file_type {file_type} in {self.__name} DAQ.")
        if file_type in ['pickle', 'json', 'csv', 'numpy', 'npy', 'toml', 'tif']:
             data = load_file(Path(shot_filepath), file_type=file_type)
        elif file_type == 'asc':
            data = self.load_asc(Path(shot_filepath))
        else:
            raise ValueError(f"Error: file_type {file_type} not supported in {self.__name} DAQ.")

        return data

    def get_shot_data(self, diag_name, shot_dict):
        """Provides shot_data depending on the data_type or data_ext of the diagnostic.
        For images, uses load_csv_image() to load the data, and for other data types, 
        uses load_data().
        """

        # MM: TODO: add sanity checks for the config parameters that we need to do this, and add error handling if they are not present. Also, add error handling for the loading functions.
        
        diag_config = self.ex.diags[diag_name].config
        data_type = diag_config['data_type']
        diag_data_path = os.path.join(Path(self.data_folder), Path(diag_config['data_folder'].lstrip("/\\")))
        
        shot_data = [] # for now, just return an array, but we could also return a dictionary with the data and the coordinates for images, for example. Or just return the raw data and let the diagnostic handle it?
        shot_filepaths = [] # intermediate array of all relevant (absolute) filepaths

        if not (data_type in self.supported_file_types):
            raise ValueError(f"Error: data_type '{data_type}' not supported in {self.__name} DAQ.")

        # Double check if shot_dict is dictionary; could just be filepath
        if isinstance(shot_dict, dict):
            # Possible shot_dict keys: filename, timestamp, timeframe, shotnumber, burst            
            required = ['filename', 'timestamp', 'timeframe', 'shotnumber', 'burst']
            if not any(key in shot_dict for key in required):
                raise ValueError(f"Error: shot_dict {shot_dict} is not a valid input for "
                                 f"get_shot_data() in {self.__name} DAQ. Please provide "
                                 f"either a dictionary with keys 'filenames' or 'timestamp', "
                                 f"or a raw filepath string.")

            print(f"Getting shot data for {diag_name} with shot_dict: {shot_dict}")

            if 'filename' in shot_dict:
                in_files = shot_dict['filename']
                for file in in_files:
                    shot_filepaths.append(os.path.join(diag_data_path, Path(file.lstrip("/\\"))))
            
            elif 'timestamp' in shot_dict:
                # Attempt to find file with timestamp in name
                self.todo('timestamp')
            
            elif 'timeframe' in shot_dict:
                # Attempt to find files with timestamps in name that fall within
                # provided timeframe
                self.todo('timeframe')
            
            elif 'shotnumber' in shot_dict:
                # Attempt to find file with shotnumber in name, or metadata that
                # matches provided shotnumber (lookup shotnumber in metadata, find
                # timestamp, find file with timestamp in name)
                self.todo('shotnumber_to_timestamp')
                self.todo('shotnumber')
            
            elif 'burst' in shot_dict:
                # Attempt to find files with burst number in name, or metadata that
                # matches provided burst number (lookup burst number in metadata,
                # find timestamp, find file with timestamp in name)
                self.todo('burst')
                
        # A single (relative) filepath can be provided as a string
        elif isinstance(shot_dict, str):
            shot_filepaths = [os.path.join(diag_data_path, Path(shot_dict))]
        
        else:
            raise ValueError(f"Error: shot_dict {shot_dict} is not a valid input for "
                             f"get_shot_data() in {self.__name} DAQ. Please provide either "
                             f"a dictionary with keys 'filenames', 'timestamp', 'timeframe', "
                             f"'shotnumber', or 'burst', or a raw filepath string.")

        for shot_filepath in shot_filepaths:
            if os.path.exists(shot_filepath):
                print(data_type)
                print(shot_filepath)
                shot_data.append(self.load_data(shot_filepath, data_type))
            else:
                print(f"Error: Could not find file {shot_filepath} for {diag_name}")
                shot_data.append(None)

        if len(shot_data) == 0:
            print(f"Warning: No shot data loaded for diagnostic {diag_name} with "
                  f"shot_dict {shot_dict}! Does the file exist?")
        
        return shot_data


    def get_files(self, timestamp_slice)->dict[str, str]:
        """Returns a list of file names in the provided directory, so long as the files contain the appropriate extension.
        
        Returns
        -------
            files_dict_sorted : dict[str, str]
                Dictionary of files and timestamps, sorted in reverse-chronological order by timestamp. The KEY is the timestamp,
                the VALUE is the filename.
        """

        diag_config = self.ex.diags[diag_name].config['setup']
        
        required = ['data_stem','data_ext','data_type']
        for param in required:
            if param not in diag_config:
                print(f"get_shot_data() error: {self.__name} DAQ requires a config['setup'] parameter '{param}' for {diag_name}")
                return None
           
        
        # Select the appropriate file extension
        extension = diag_config['data_ext']#self.input["EXTENSION_DICT"][self.input["DEVICE_NAME"]]

        # Accumulate list of files with the correct extension in the directory provided.
        #timestamp_slice = self.input["TIMESTAMP_SLICE"][self.input["DEVICE_NAME"]] # slice we need to take from the string to get the timestamp
        
        # Create dictionary of files and their timestamps. If we have no pre-determined means of doing this, fall back on using os.stat().st_mtime. The dictionaries are of form {Timestamp:Slice}
        if timestamp_slice is not None:
            files_dict = {f[timestamp_slice[0]:timestamp_slice[1]]:f for f in os.listdir(diag_config['paths']['data_folder']) if f.endswith(extension)\
                    and not os.path.isdir(os.path.join(diag_config['paths']['data_folder'], f))}
        else:
            logger.info(f"Warning: no timestamp slice provided for {self.ex.diags[diag_name]}")
            files_dict = {str(int(os.stat(os.path.join(diag_config['paths']['data_folder'], f)).st_mtime)):f for f in os.listdir(diag_config['paths']['data_folder']) if f.endswith(extension)\
                    and not os.path.isdir(os.path.join(diag_config['paths']['data_folder'], f))}
        

        # Sort the files in reverse order to their timestamps (i.e. most recent files are earlier in the list)
        files_dict_sorted = dict(sorted(files_dict.items(), key=lambda item : item[0], reverse=True))
        # make sure that we are not asking for a larger number of shots than actually exist ...
            
        if len(self.input["EXP_SHOT_NOS"]) > len(files_dict_sorted.values()):
            no_of_req_shots = len(self.input["EXP_SHOT_NOS"])
            no_of_files = len(files_dict_sorted)
            raise ValueError(f"Error: requested {no_of_req_shots} shots, but only {no_of_files} were found.")
            

        return files_dict_sorted
        
        
    def get_supplementary_files(self, files_dict_in):
         #        "SUPPLEMENTARY_FOLDER_NAMES":SUPPLEMENTARY_FOLDER_NAMES,
            
            # Select the appropriate file extension
        extension = self.input["EXTENSION_DICT"][self.input["DEVICE_NAME"]]

        # Accumulate list of files with the correct extension in the directory provided.
        timestamp_slice = self.input["TIMESTAMP_SLICE"][self.input["DEVICE_NAME"]] # slice we need to take from the string to get the timestamp
        
        # Create dictionary of files and their timestamps. If we have no pre-determined means of doing this, fall back on using os.stat().st_mtime. The dictionaries are of form {Timestamp:Slice}
        for folder in self.input["SUPPLEMENTARY_FOLDER_NAMES"][self.input["DEVICE_NAME"]]:
            path=os.path.join(self.input["PARENT_DIR"], folder)
            for f in os.listdir(path):
                
                if f.endswith(extension) and not os.path.isdir(os.path.join(path, f)):
                    if timestamp_slice is not None:
                        files_dict_in[f[timestamp_slice[0]:timestamp_slice[1]]]=os.path.join(path, f)
                    else:
                        logger.info(f"Warning: no timestamp slice provided for {self.input['DEVICE_NAME']}")
                        files_dict_in[str(int(os.stat(os.path.join(path, f)).st_mtime))]=os.path.join(path, f)
                
        files_dict_sorted = dict(sorted(files_dict_in.items(), key=lambda item : item[0], reverse=True))
        
        return files_dict_sorted
    

    def build_time_point(self, shot_dict):
        """Universal function to return a point in time for DAQ, for comparison, say in calibrations
        """
        if isinstance(shot_dict['shot'], list):
            return int(str(np.max(shot_dict['shot']))[0:10])
        else:
            return int(str(shot_dict['shot'])[0:10])# time_point

    def timestamp_to_filename(self, timestamp):
        raise NotImplementedError("timestamp_to_filename() not implemented yet")
    
    def timeframe_to_filenames(self, timeframe):
        raise NotImplementedError("timeframe_to_filenames() not implemented yet")
    
    def burst_to_filename(self, burst):
        raise NotImplementedError("burst_to_filename() not implemented yet")
    
    def todo(self, item):
        print(f"TODO: {item} functionality not implemented yet in {self.__name} DAQ.")
    
