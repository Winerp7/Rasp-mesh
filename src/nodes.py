from mesh import MeshNet
from utils import get_serial, delay, Timer, from_json, to_json, force_reboot
from functionality import Functionality
import requests

class SlaveNode:
    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.id = get_serial()
        self.functionality = None

    def init_node(self):
        message_dict = {'type': 'init', 'id': self.id}
        init_message = to_json(message_dict)
        self.mesh.send_message(init_message)
    
    def run(self):
        self.mesh.on_messsage(self.message_handler)
        self.init_node()

        timer = Timer()
        
        while True: 
            self.mesh.update()

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = from_json(message)

        if message_dict['type'] == 'init':
            self.confirmed = message_dict['confirmed']

        elif message_dict['type'] == 'update':
            has_succeeded = self.try_update(message_dict)
            response_dict = {'type': 'update-confirm', 'success': has_succeeded}
            confirm_message = to_json(response_dict)
            self.mesh.send_message(confirm_message)
                
    def try_update(self, message_dict):
        # TODO: figure out whether this should be saved in a file

        if message_dict['reboot']:
            force_reboot()

        if self.functionality is not None:
            self.functionality.stop()
        
        if message_dict['sleep']:
            return True
    
        setup, loop = message_dict['setup'], message_dict['loop']
        func_is_working = Functionality.test_functionality(setup, loop)
        
        if func_is_working:
            self.functionality = Functionality(setup, loop, self.mesh)
            self.functionality.start()
        
        return func_is_working

    
    def create_data_message(self):
        message_dict = {'type': 'data', 'values': ['what', 'the', 'fuck']}
        message = to_json(message_dict)
        return message

class MasterNode:
    UPDATE_INTERVAL = 1000

    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.id = get_serial()
        self.nodes = {'00000000e86aa86c': 
            {
                'setup': '',
                'loop': 'upload({"sensor": "DHT", "value": 22.3})\nwait(5000)',
                'reboot': False,
                'sleep': False,
            }
        }  # TODO: dont hard code

    def init_master(self):
        pass # TODO: init master on server

    def run(self):
        self.mesh.on_messsage(self.message_handler)
        self.init_master()

        timer = Timer()

        while True:
            self.mesh.update()

            if timer.time_passed() > MasterNode.UPDATE_INTERVAL:
                self.fetch_updates()
                timer.reset()


    def fetch_updates(self): # TODO, get /update from server
        pass

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = from_json(message)

        if message_dict['type'] == 'init':
            _id = message_dict['id']
            if _id in self.nodes:
                self.send_update(_id)
            else:
                self.new_node(message_dict['id'])

        if message_dict['type'] == 'data': # TODO: send data to server
            pass
        
        if message_dict['type'] == 'update-confirm': # TODO: change update state of the node
            update_succeeded = message_dict['success']
            # send back to server

    def new_node(self, _id):
        pass # TODO: init node on server
        # Add to some list of nodes

    def send_update(self, _id):
        status = self.nodes[_id]
        message_dict = {'type': 'update', **status}
        update_message = to_json(message_dict)
        self.mesh.send_message(update_message)


    
