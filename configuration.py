import configparser

class Calibration():
    def __init__(self):
        self.gravity_offset=0.0
        self.gravity_gain=1.0
        self.temperature_offset=0.0
        self.temperature_gain=1.0
        self.battery_offset=0.0
        self.battery_gain=1.0

class Configuration():
    def __init__(self):
        self.interval=900
        self.maxinterval=30
        self.fahrenheit=False
        self.mfilter=3
        self.average=0
        self.path='.'
        self.size=24*4*31
        self.debug=False
        self.calibration={}

    def Write(self,filename):
        config=configparser.ConfigParser()
        config['common']={}
        config['common']['interval']=str(self.interval)
        config['common']['maxinterval']=str(self.maxinterval)
        config['common']['fahrenheit']=str(self.fahrenheit)
        config['common']['mfilter']=str(self.mfilter)
        config['common']['average']=str(self.average)
        config['common']['path']=str(self.path)
        config['common']['size']=str(self.size)
        config['common']['debug']=str(self.debug)
        with open(filename,'w') as configfile:
            config.write(configfile)

    def Read(self,filename):
        config=configparser.ConfigParser()
        config.read(filename)
        for section in config.sections():
            if section=='common':
                for key in config[section]:
                    if key=='interval':             self.interval=config[section].getint(key)
                    elif key=='maxinterval':        self.maxinterval=config[section].getint(key)
                    elif key=='fahrenheit':         self.fahrenheit=config[section].getboolean(key)
                    elif key=='mfilter':            self.mfilter=config[section].getint(key)
                    elif key=='average':            self.average=config[section].getint(key)
                    elif key=='size':               self.size=config[section].getint(key)
                    elif key=='debug':              self.debug=config[section].getboolean(key)
                    elif key=='path':               self.path=config[section][key]
                    else:
                        print('Unknown key "'+str(key)+'" in common')
                        return False
            else:
                if not section in self.calibration:
                    self.calibration[section]=Calibration()
                for key in config[section]:
                    if key=='gravity_offset':       self.calibration[section].gravity_offset=config[section].getfloat(key)
                    elif key=='gravity_gain':       self.calibration[section].gravity_gain=config[section].getfloat(key)
                    elif key=='temperature_offset': self.calibration[section].temperature_offset=config[section].getfloat(key)
                    elif key=='temperature_gain':   self.calibration[section].temperature_gain=config[section].getfloat(key)
                    elif key=='battery_offset':     self.calibration[section].battery_offset=config[section].getfloat(key)
                    elif key=='battery_gain':       self.calibration[section].battery_gain=config[section].getfloat(key)
                    else:
                        print('Unknown key "'+key+'" in '+section)
                        return False
        return True

