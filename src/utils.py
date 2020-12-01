from time import sleep, time
import subprocess
import json

def delay(ms):
    sleep(ms/1000.0)
    
def delete_dhcplist():
	subprocess.call(['sudo', 'rm', 'dhcplist.txt'])

def get_serial():
	# Extract serial from cpuinfo file
	cpuserial = "0000000000000000"
	try:
		f = open('/proc/cpuinfo','r')
		for line in f:
			if line[0:6]=='Serial':
				cpuserial = line[10:26]
		f.close()
	except:
		cpuserial = "ERROR000000000"

	return cpuserial

def force_reboot():
	subprocess.call(['sudo', 'reboot'])

def dict_to_json_string(py_object):
	json_object = json.dumps(py_object)
	return str(json_object)

def json_string_to_dict(json_string):
	return json.loads(json_string)

def string_to_bool(string):
	return string in ['true', 'True']

class Timer:
	def __init__(self):
		self.start = time()

	def time_passed(self):
		return int((time()-self.start)*1000) % (2 ** 32)

	def reset(self):
		self.start = time()


	
