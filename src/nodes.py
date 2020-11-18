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
    UPDATE_INTERVAL = 60000

    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.id = get_serial()
        self.sensor_data = {}
        self.nodes = []
        self.nodes_config = {'00000000e86aa86c': 
            {
                'setup': '',
                'loop': 'upload({"sensor": "DHT", "value": 22.3})\nwait(5000)',
                'reboot': False,
                'sleep': False,
            }
        }  # TODO: dont hard code

    def init_master(self):
        init_dict = { 'nodeID': _id, 'status': 'Online', 'isMaster': True}
        message = to_json(init_dict)
        self.post_request('initNode', message)

    def run(self):
        self.mesh.on_messsage(self.message_handler)
        self.init_master()

        timer = Timer()

        while True:
            self.mesh.update()

            if timer.time_passed() > MasterNode.UPDATE_INTERVAL:
                self.fetch_functionality()
                timer.reset()


    def fetch_functionality(self): 
        try:
            updates = self.get_request('getFunctionality', {'email': 'jens@mytest.com'}).json()
            for node in updates:
                _id = node['nodeID']
                body = node['body']
                self.nodes_config[_id] = body
                self.send_update(_id)
        except Exception as e:
            print("No updates for your slaves")

    def message_handler(self, from_node, message):
        print(message, flush=True)
        message_dict = from_json(message)

        if message_dict['type'] == 'init':
            _id = message_dict['id']
            if _id in self.nodes_config:
                self.send_update(_id)
            else:
                self.new_node(message_dict['id'])

        if message_dict['type'] == 'data': 
            _id = message_dict['id']
            sensor_values = message_dict['sensor-values']
            if _id  in self.sensor_data:
                self.sensor_data[_id].append(sensor_values)
            else:
                self.sensor_data[_id] = [sensor_values]


        if message_dict['type'] == 'update-confirm': # TODO: change update state of the node
            update_succeeded = message_dict['success']
            # send back to server

    def new_node(self, _id):
        self.nodes.append(_id)
        init_dict = { 'nodeID': _id, 'status': 'Online'}
        message = to_json(init_dict)
        self.post_request('initNode', message)

    def send_update(self, _id):
        status = self.nodes_config[_id]
        message_dict = {'type': 'update', **status}
        update_message = to_json(message_dict)
        self.mesh.send_message(update_message)

    def post_sensor_data(self):
        message = to_json(self.sensor_data)
        response = self.post_request('updateSensorData', message)
        if response is not None and response.ok:
            self.sensor_data.clear()
        

    def create_url(self, path):
        return 'http://localhost:3000/pi/' + path 

    def post_request(self, path, message):
        url = create_url(path)
        response = None
        try:
            response = requests.post(url, json=message)
        except Exception as e:
            print(e)
        return response


    def get_request(self, path, message):
        url = create_url(path)
        response = None
        try:
            response = requests.get(url, json=message)
        except Exception as e:
            print(e)
        return response
        
