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
        
        while True: 
            self.mesh.update()

            if self.confirmed:
                message_dict = {'type': 'data', 'values': ['what', 'the', 'fuck']}
                if timer.time_passed() >= 1000:
                    self.mesh.send_message(message)
                    timer.reset()


class MasterNode:
    UPDATE_INTERVAL = 1000

    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.new_nodes = []

    def init_node(self):
        # init node on server
        message_dict = {'type': 'init', 'confirmed': True}
        init_message = dict_to_json_string(message_dict)
        self.mesh.send_message(init_message)

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = json_string_to_dict(message)

        if message_dict['type'] == 'init':
            self.init_node()
            new_node = message_dict['id']

        if message_dict['type'] == 'data': # TODO
            pass
        
        if message_dict['type'] == 'update-confirm':
            pass
        
    
    def fetch_updates(self): # TODO, get /update from server
        pass

    def run(self):
        self.mesh.on_messsage(self.message_handler)

        timer = Timer()

        while True:
            self.mesh.update()

            if timer.time_passed() > MasterNode.UPDATE_INTERVAL:
                self.fetch_updates()
                timer.reset()

