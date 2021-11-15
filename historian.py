#!/usr/bin/env python3
#
# JSON server for collecting and sharing data over http-port
#
from datetime import datetime
import time,json,os,csv,copy


# Dataset holder
class dataset():
    def __init__(self):
        self.time=time.time()
        self.temperature=0.0
        self.battery=0.0
        self.gravity=0.0

# Custom httpd handler
class Historian():
    def __init__(self,path,mfilter,average,size,maxinterval,fahrenheit,debug):
        self.interval=900
        self.maxinterval=maxinterval
        self.fahrenheit=fahrenheit
        self.mfilter=mfilter
        self.average=average
        self.path=path
        self.size=size
        self.debug=debug
        self.data={}
        self.mdata={}
        self.start=0
        self.fd=0

        # Limit interval
        if self.interval<self.maxinterval:
            self.interval=self.maxinterval

        # Sanitize path and assert trailing slash
        if len(self.path) and not self.path[-1:]=='/':
            self.path=self.path+'/'

        # Load dataset from existing files
        if len(self.path):
            self.Reload()

    def Reload(self):
        # Find existing files in path
        files=[]
        for filename in os.listdir(self.path):
            if filename.upper().startswith('BREWTREND-'):
                if filename.upper().endswith('.CSV'):
                    files.append(self.path+filename)
        files=sorted(files)

        # Read historical data from existing files
        rows=[]
        for filename in files:
            if self.debug: print('Reading data from '+filename)
            with open(filename,'r') as csvfile:
                csvdata=csv.reader(csvfile)
                try:
                    csvrows=[]
                    next(csvdata)
                    for row in csvdata:
                        if len(csvrows)>self.size: csvrows=csvrows[1:]
                        csvrows.append(row)
                    rows.extend(csvrows)
                    while len(rows)>self.size:
                        rows=rows[1:]
                except Exception as e:
                    print('Error: '+str(e))

        # Put historical data in current dataset
        for data in rows:
            obj=dataset()
            obj.time=float(data[0])
            obj.gravity=float(data[2])
            obj.temperature=float(data[3])
            obj.battery=float(data[4])
            self.AddSample(data[1],obj)

        # Report result
        if self.debug:
            if len(self.data):
                print('Read back historical data:')
            for name in self.data:
                print(name+': '+str(len(self.data[name]))+' datasets')


    def AddSample(self,name,data):
        # Add dataset
        if not name in self.data:
            self.data[name]=[]
        while len(self.data[name])>self.size:
            self.data[name]=self.data[name][1:]
        self.data[name].append(data)

        # Median filter output
        if self.mfilter>1:
            if not name in self.mdata:
                self.mdata[name]=[]
            self.mdata[name].append(copy.copy(data))
            if len(self.mdata[name])>=self.mfilter:
                gravity=[]
                temperature=[]
                battery=[]
                for x in self.mdata[name]:
                    gravity.append(x.gravity)
                    temperature.append(x.temperature)
                    battery.append(x.battery)
                gravity=sorted(gravity)
                temperature=sorted(temperature)
                battery=sorted(battery)
                data.gravity=gravity[int(self.mfilter/2)]
                data.temperature=temperature[int(self.mfilter/2)]
                data.battery=battery[int(self.mfilter/2)]
                self.mdata[name]=self.mdata[name][1:]

        # Lowpass filter output
        if self.average>1:
            if len(self.data[name])>=self.average:
                n=self.average
            else:
                n=len(self.data[name])
            sum_gravity=0
            sum_temperature=0
            sum_battery=0
            for i in range(len(self.data[name])-n,len(self.data[name])):
                sum_gravity+=self.data[name][i].gravity
                sum_temperature+=self.data[name][i].temperature
                sum_battery+=self.data[name][i].battery
            data.gravity=sum_gravity/n
            data.temperature=sum_temperature/n
            data.battery=sum_battery/n

    def ParseSpindel(self,jsondata):
        if self.debug:  print('Parsing iSpindel data: '+str(jsondata))
        name=jsondata['name']
        data=dataset()
        data.temperature=float(jsondata['temperature'])
        data.battery=float(jsondata['battery'])
        data.gravity=float(jsondata['gravity'])
        #data.id=jsondata['ID']
        #data.angle=jsondata['angle']
        #data.tunit=jsondata['temp_units']
        if self.fahrenheit==False and not jsondata['temp_units']=='C':
            data.temperature=(data.temperature-32)/1.8
        if self.fahrenheit==True and jsondata['temp_units']=='C':
            data.temperature=data.temperature*1.8+32
        if int(jsondata['interval'])<self.interval:
            self.interval=int(jsondata['interval'])
        if self.interval<self.maxinterval:
            self.interval=self.maxinterval
        return name,data

    def ParseTilt(self,jsondata):
        if self.debug: print('Parsing Tilt data: '+str(jsondata))
        name='Tilt '+jsondata['Color']
        data=dataset()
        data.temperature=float(jsondata['Temp'])
        data.gravity=float(jsondata['SG'])
        #data.time=float(jsondata['Timepoint'])
        #data.beer=jsondata['Beer']
        #data.comment=jsondata['Comment']
        if not self.fahrenheit:
            data.temperature=(data.temperature-32)/1.8

        return name,data

    def Parse(self,string):
        ## Parse POST data
        name=''
        data=None
        try:
            jsondata=json.loads(string)
            if 'Color' in jsondata:
                name,data=self.ParseTilt(jsondata)
            else:
                name,data=self.ParseSpindel(jsondata)
        except Exception as e:
            print('Parser exception: '+str(e))
            print('Failed to parse input data: '+str(string))

        if len(name) and data:
            # Drop old files regularly
            if self.start+3600*24*7<time.time():
                if self.fd:
                    self.fd.close()
                    self.fd=0

            # Create log files with headers as necessary
            if len(self.path) and not self.fd:
                stamp=datetime.now().strftime("%Y%m%d%H%M")
                filename=self.path+'BREWTREND-'+stamp+'.CSV'
                self.fd=open(filename,'w')
                if self.fd:
                    if self.debug: print('Creating new logfile: '+filename)
                    self.fd.write('Time,Device,Gravity,Temperature,Battery\n')
                    self.start=time.time()
                else:
                    print('Cannot write to path: '+filename)        

            # Write data to logfile
            if self.fd:
                csvdata=str(data.time)+','
                csvdata+=str(name)+','
                csvdata+=str(data.gravity)+','
                csvdata+=str(data.temperature)+','
                csvdata+=str(data.battery)+'\n'
                self.fd.write(csvdata)
                self.fd.flush()

            # Add sample to buffers
            self.AddSample(name,data)

        return '{}'

