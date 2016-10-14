import os, sys
import requests
import datetime
import webbrowser
import psutil
#from PIL import Image
#from PIL import ImageTk
import random

BASE = "/sys/class/backlight/rpi_backlight/"

#######################


#---------------------------
#------USER FUNCTIONS-------
#---------------------------

def slideshow_info(val, params, action):
	if action == 'onclick':
		return [True, True]
	return [True, True]

def slideshow(val, params, action):
	directory = "photos"
	if 'directory' in params:
		directory = params['directory']
	if action == 'onconfigure':
		dirlist = os.listdir(directory)
		random.shuffle(dirlist)
		val = [dirlist, 0]
	if val[1] == len(val[0]):
		random.shuffle(val[0])
		val[1] = 0
	f = directory + val[0][val[1]]
	val[1] += 1
	return [val, True, {'image': f}]

#def web(val, params, action):
#	if (action == "onclick"):
#		webbrowser.get('epiphany').open('http://192.168.1.74:8084',0, True)
#	return [val, True]

def brightness_switch(val, params, action):
	if action == 'onclick':
		if val>=128:
			brightness(0)
			return [0, False]
		else:
			brightness(255)
			return [255, True]
	val = int(brightness())
	return [val, val>=128]

def openweathermap(val, params, action):
	query = 'q=paris,fr'
	if 'city' in params:
		query = "q="+params['city']
	if 'id' in params:
		query = "id="+params['id']
	try:
		r = requests.get("http://api.openweathermap.org/data/2.5/weather?"+query+"&appid="+params['appid'])
		data=r.json()
		icon = "http://openweathermap.org/img/w/"+data['weather'][0]['icon']+".png"
		label = data['name']+"\n"+data['weather'][0]['main']
		return [1, True, {'icon': icon, 'label': label}]
	except:
		return [1, True, {'icon': 'weather.station.gif', 'label': 'error'}]
	
def clock(val, params, action):
	fmt = "%A\n%d %B\n\n%H:%M"
	#option = ['', 'a', 'b', 'c']
	if params != None and 'fmt' in params:
		fmt = params['fmt']
	if action == "onconfigure":
		val = 0
	#val += 1
	#if (val==4):
	#	val = 1
	#fmt += " ["+option[val]+"]"
	ret = datetime.datetime.now().strftime(fmt)
	return [val, True, {'label': ret}]
	
def domodevices(val, params, action):
    try:
    	id = params['id']
    	param = params['param']
    	response = requests.get(params['domo_url']+"/json.htm?type=devices&param="+param+"&rid="+id)
    	json_obj = response.json()
    	txt = str(json_obj['result'][0]['Temp'])+" C"
    except:
    	txt = 'error'
    return [txt, True, {'label': txt}]

def domoswitch(val, params, action):
    try:
    	id = params['id']
    	if action == 'onclick':
    		response = requests.get(params['domo_url']+"/json.htm?type=command&param=switchlight&idx="+id+"&switchcmd=Toggle")
    		val = not val
    	else:
    		response = requests.get(params['domo_url']+"/json.htm?type=devices&rid="+id)
    		data=response.json()
    		if data['result'][0]['Status'] == 'On':
    			val = True
    		else:
    			val = False
    except:
    	return [val, val, {'label': 'error'}]
    return [val, val]
    
def raspberrypi(val, params, action):
	memory = psutil.virtual_memory()
	disk = psutil.disk_usage('/')
	boottime = datetime.datetime.fromtimestamp(psutil.boot_time())
	tmp = datetime.datetime.now() - boottime
	#time = divmod(tmp.days * 86400 + tmp.seconds, 60)
	txt = "CPU temp: "+str(getCPUtemperature())+" C\n"
	txt += "RAM free: "+str(round(memory.available/1024.0/1024.0,1))+" Mo\n"
	txt += "CPU used: "+str(psutil.cpu_percent())+" %\n" 
	txt += "Disk free: "+str(round(disk.free/1024.0/1024.0/1024.0,1))+" Go\n"
	txt += "Boot: "+str(tmp.days)+" j "+str(int(tmp.seconds/3600))+" h"
	return ['', True, {'label': txt}]

def quit(val, params, action):
	if action == 'onclick':
		sys.exit(0)
	return ['', True]
     
#---------------------------
#------USER TOOLS-----------
#---------------------------

# Change screen brightness    
def brightness(value = -1):
	_brightness = open(os.path.join(BASE,"brightness"), "w+")
	if value >= 0 and value < 256:
		_brightness.write(str(value))
		_brightness.close()
		return
	elif value == -1:
		ret = _brightness.read()
		_brightness.close()
		return ret
	_brightness.close()
	raise TypeError("Brightness should be between 0 and 255")

# Return CPU temperature as a character string                                      
def getCPUtemperature():
    res = os.popen('/usr/bin/vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

