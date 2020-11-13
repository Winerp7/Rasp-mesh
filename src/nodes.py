from mesh import MeshNet
from utils import get_serial, delay, Timer, from_json, to_json, force_reboot
from functionality import Functionality
import requests

class SlaveNode:
    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.confirmed = False
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

            if self.confirmed:
                if timer.time_passed() >= 1000:
                    message = self.create_data_message()
                    self.mesh.send_message(message)
                    timer.reset()

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = from_json(message)

        if message_dict['type'] == 'init':
            self.confirmed = message_dict['confirmed']

        elif message_dict['type'] == 'update':
            has_succeeded = self.try_update()
            message_dict = {'type': 'update-confirm', 'success': has_succeeded}
            confirm_message = to_json(message_dict)
            self.mesh.send_message(confirm_message)
            
            
    def try_update(self, message_dict):
        setup, loop = message_dict['setup'], message_dict['loop']
        # TODO: figure out whether this should be saved in a file

        if message_dict['reboot']:
            force_reboot()

        if self.functionality is not None:
            self.functionality.stop()
        
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
        self.new_nodes = []

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
            self.new_node()

        if message_dict['type'] == 'data': # TODO: send data to server
            pass
        
        if message_dict['type'] == 'update-confirm': # TODO: change update state of the node
            update_succeeded = message_dict['success']
            # send back to server

    def new_node(self):
        # TODO: init node on server
        message_dict = {'type': 'init', 'confirmed': True}
        init_message = to_json(message_dict)
        self.mesh.send_message(init_message)
    
