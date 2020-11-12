from mesh import MeshNet
from utils import get_serial, delay, Timer, json_string_to_dict, dict_to_json_string
import requests

class SlaveNode:
    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.confirmed = False
        self.id = get_serial()

    def init_node(self):
        message_dict = {'type': 'init', 'id': self.id}
        init_message = dict_to_json_string(message_dict)
        self.mesh.send_message(init_message)

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = json_string_to_dict(message)

        if message_dict['type'] == 'init':
            self.confirmed = message_dict['confirmed']

        elif message_dict['type'] == 'update':
            pass
        
    def run(self):
        self.mesh.on_messsage(self.message_handler)
        self.init_node()

        timer = Timer()

        message = 'I am confirmed' if self.confirmed else 'i am not confirmed'
        
        while True: 
            self.mesh.update()

            if timer.time_passed() >= 1000:
                #self.mesh.send_message(message)
                timer.reset()


class MasterNode:
    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.new_nodes = []

    def init_response(self):
        message_dict = {'type': 'init', 'confirmed': self.id}
        init_message = dict_to_json_string(message_dict)
        self.mesh.send_message(init_message)

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = json_string_to_dict(message)

        if message_dict['type'] == 'init':
            self.init_response()
            new_node = message_dict['id']
            self.new_nodes.append(new_node)

        if message_dict['type'] == 'data': # TODO
            pass
            
        self.mesh.send_message(message)
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