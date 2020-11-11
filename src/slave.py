from mesh import MeshNet
from utils import delay, Timer
from struct import *


class SlaveNode:
    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.confirmed = False

    def init_node(self):
        init_message = 'init'
        self.mesh.send_message(message)

    def message_handler(from_node, message):
        print(message)
        
    def run(self):
        self.mesh.on_messsage(self.message_handler)
        
        timer = Timer()

        message = 'Hello this string is not too big'
        
        while True: 
            mesh.update()

            if timer.time_passed() >= 1000:
                mesh.send_message(message)



if __name__ == '__main__':
    slave = SlaveNode()
    slave.run()
