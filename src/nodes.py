from mesh import MeshNet
from utils import delay, Timer
import requests


class SlaveNode:
    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.confirmed = False

    def init_node(self):
        init_message = 'init'
        self.mesh.send_message(message)

    def message_handler(self, from_node, message):
        print(message)
        
    def run(self):
        self.mesh.on_messsage(self.message_handler)

        timer = Timer()

        message = 'Hello'
        
        while True: 
            self.mesh.update()

            if timer.time_passed() >= 1000:
                self.mesh.send_message(message)
                timer.reset()


class MasterNode:
    def __init__(self):
        self.mesh = MeshNet(master=True)

    def message_handler(self, from_node, message):
        print(message, flush=True)
        try:
            r = requests.post('http://192.168.43.105:3000/api-test', data = {'id': message})
            print(r.status_code, flush=True)
            if r.status_code == 200:
                print(r.text, flush=True)
        except:
            print('Failed to contact server')

    def run(self):
        self.mesh.on_messsage(self.message_handler)

        while True:
            self.mesh.update()