import os, sys
from pathlib import Path
import csv
import re
import numpy as np
from LAMP.DAQ import DAQ

class FireballIII(DAQ):
    """Interface layer for HRMT68
    """
#data_folder
    __version = 0.1
    __name = 'HRMT68'
    __authors = ['Brendan Kettle', 'Eva Los']

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


    def get_shot_data(self, diag_name, shot_dict):

        diag_config = self.ex.diags[diag_name].config

        # Double check if shot_dict is dictionary; could just be filepath
        if isinstance(shot_dict, dict):
        
            required = ['data_stem','data_ext','data_type']
            for param in required:
                if param not in diag_config:
                    print(f"get_shot_data() error: {self.__name} DAQ requires a config['setup'] parameter '{param}' for {diag_name}")
                    return None
    
            filepath=self.data_folder+diag_config['data_folder']
            csv_files = np.array([f for f in os.listdir(filepath) if f.endswith(diag_config['data_ext']) and f.startswith(diag_config['data_stem'])])
                
            
            parts = np.array([int(filename.replace('.csv', '').split('_')[4][0:10]) for filename in csv_files])
            
            print(f"shot_dict: {shot_dict}")
            print(f"parts: {parts}")




            #shot_no_=shot_dict["shot"]
            closest_indxs=np.array([np.argmin(abs(parts-int(str(shot_no)[0:10]))) for shot_no in shot_dict["shot"]])

            in_files=csv_files[closest_indxs]

            for file in in_files:
  
                shot_filepath=filepath+file
                if diag_config['data_type'] == 'image':
                    shot_data = self.load_imdata(shot_filepath)
#                 else:
#                     print('Non-image data loading not yet supported... probably need to add text at least?')

                elif diag_config['data_type'] == 'csv':
                    shot_data = np.array(self.load_csv_image(shot_filepath)["IMG"])
                else:
                    print('Non-image data loading not yet supported... probably need to add text at least?')


        # raw filepath?
        else:
            # look for file first
            shot_filepath = os.path.join(Path(self.data_folder), Path(shot_dict.lstrip(r'\/')))
            if os.path.exists(shot_filepath):
                filepath_no_ext, file_ext = os.path.splitext(shot_filepath)
                img_exts = {".tif",".tiff"}
                # if it's there, try and suss out data type from file extension
                if file_ext in img_exts:
                    shot_data = self.load_imdata(shot_filepath)
                else:
                    print(f"Error; get_shot_data(); could not identify file type for extension: {file_ext}")
            else:
                print(f"Error; get_shot_data(); could not find shot with raw filepath: {shot_filepath}")
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
   