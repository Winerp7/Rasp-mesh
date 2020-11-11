from mesh import MeshNet

from struct import unpack
import requests

class MasterNode:
    def __init__(self):
        self.mesh = MeshNet(master=True)

    def message_handler(from_node, message):
        print(message, flush=True)
        '''
        try:
            r = requests.post('http://192.168.43.105:3000/api-test', data = {'id': message})
            print(r.status_code, flush=True)
            if r.status_code == 200:
                print(r.text, flush=True)
        except:
            print('Failed to contact server')
        '''

    def run(self):
        self.mesh.on_messsage(self.message_handler)

        while True:
            self.mesh.update()


if __name__ == '__main__':
    master = MasterNode()
    master.run()
