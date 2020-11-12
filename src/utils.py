from time import sleep, time
import subprocess
import json

def delay(ms):
    sleep(ms/1000.0)
    
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


def dict_to_json_string(dictionary):
	json_object = json.dumps(dictionary)
	return str(json_object)

def json_string_to_dict(json_string):
	return json.loads(json_string)


class Timer:
	def __init__(self):
		self.start = time()

	def time_passed(self):
		return int((time()-self.start)*1000) % (2 ** 32)

	def reset(self):
		self.start = time()


	
