# brewtrend
Logs and plots data from tilt and ispindel devices in a interactive gui hosted on your own LAN. It's written in python so it works well on windows as well as low-powered soc-systems such as raspberry pi or beaglebone black.

# Installation
First install a python3 distribution of your choice, winpython works well for windows users, linux/mac users can use what ships with their OS.
Then you need to install some dependencies:
python -m pip install dash dash_bootstrap_components dash_daq
Finally you can run the server application:

python brewtrend.py --port 80 --config brewtrend.ini

Please note that by default it will bind to port 80. You will either have to allow your user to do this, or use a higher port.

You can use the --help option to see additional options, and/or read brewtrend.ini for configuration options.

# Setting up tilt hydrometer
Enter http://your-ip-adress/update as your cloud URL in your tilt-app
Notice the http without s. You can use https if you want to, but this requires certificates so it's easier to just drop encryption for a LAN-only setup


![image](https://user-images.githubusercontent.com/51258725/141873108-7f8389b6-4883-434e-8300-44be31c56227.png)

# Setting up iSpindel hydrometer
Set your device in configuration mode, set service type to HTTP, enter your IP address, set port to 80 and enter /update as path/URI.


![image](https://user-images.githubusercontent.com/51258725/141873186-1e99ca4f-4f1a-494e-bef9-88374d5b0b02.png)

# Reading data
Enter your ip address directly in your browser:


![image](https://user-images.githubusercontent.com/51258725/141705419-ee34d3ca-3c69-44f0-8589-581d3d558f61.png)
