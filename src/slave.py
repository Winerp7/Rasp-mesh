from mesh import MeshNet
from utils import delay, Timer
from struct import *


class SlaveNode:
    def __init__(self):
        self.meshnet = MeshNet(master=False)
        self.confirmed = False

    def init_node(self):
        init_message = 'init'
        self.mesh.send_message(message)

    def message_handler(from_node, message):
        print(message)
        
    def run(self):
        self.mesh.on_messsage(self.message_handler)

        timer = Timer()

        message = 'Hello'
        
        while True: 
            self.meshnet.update()

            if timer.time_passed() >= 1000:
                self.meshnet.send_message(message)
                timer.reset()



if __name__ == '__main__':
    slave = SlaveNode()
    slave.run()
