# brewtrend
Logs and plots data from tilt and ispindel devices

# Installation
First install a python3 distribution of your choice, winpython works well for windows users
Then you need to install some dependencies:
python -m pip install dash dash_bootstrap_components dash_daq
Finally you can run the server application:
python monitor.py

You can use the --help option to see additional options.

# Setting up tilt hydrometer
Enter http://your-ip-adress/update as your cloud URL in your tilt-app
Notice the http without s. You can use https if you want to, but this requires certificates so it's easier to just drop encryption for a LAN-only setup

# Setting up iSpindel hydrometer
Set your device in configuration mode, set service type to HTTP-post, enter your IP address and set port to 80.

# Reading data
Enter your ip address directly in your browser:
![image](https://user-images.githubusercontent.com/51258725/141705419-ee34d3ca-3c69-44f0-8589-581d3d558f61.png)
