from time import sleep, time
import subprocess

def delay(ms):
    sleep(ms/1000.0)
    
def getserial():
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


class Timer:
	def __init__(self):
		self.start = time()

	def time_passed():
		return int((time()-self.start)*1000) % (2 ** 32)

	def reset(self):
		self.start = time()


	
