# Fireball DAQ

## Structure

### Usage

I have mainly worked on the get_shot_data() function in the DAQ, which gets called by the diagnostic through:

    def get_shot_data(self, shot_dict):
        """Wrapper for getting shot data through DAQ"""
        return self.DAQ.get_shot_data(self.config['name'], shot_dict)

Right now, the function returns a list with the data elements. [data0, data1, data2, …] which you can address with normal python syntax data[0]…

The amount of data returned depends on the shot_dict you provide:

Currently implemented:

```
shot_dict = ‘filename.ext’ # A string with the name of the file inside the data directory of the diagnostic
```

```
shot_dict = {‘filename’:[‘filename.ext’,filename2.ext’]} or shot_dict = {‘filename’: ‘filename.ext’} # key ‘filename’ with list or string entry for the filenames in data directory
```

```
shot_dict = {‘timestamp’:[‘20260212123055’,’20260215112700’, …]} or {‘timestamp’: ‘20260212123055’} # key ‘timestamp’ with list or string entry of the timestamp in the filename. This needs to be the exact timestamp in the filename right now!
```

```
shot_dict = {‘timeframe’: [‘20260212123055’,’20260215112700’]} or {‘timeframe’: [‘20260212’,’20260215’]} # key ‘timeframe’ with two timesteps start_time and end_time (in this order!). This finds all files that contain strings in between the two timesteps! This could lead to false positives if your files have a lot of numbers in them!
```