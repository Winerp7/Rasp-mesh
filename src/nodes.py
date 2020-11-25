from mesh import MeshNet
from utils import get_serial, delay, Timer, from_json, to_json, force_reboot
from functionality import Functionality
from api import Api

class SlaveNode:
    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.id = get_serial()
        self.functionality = None

    def _init_node(self):
        message_dict = {'id': self.id}
        init_message = to_json(message_dict)
        self.mesh.send_message(MeshNet.MSG_TYPE_INIT, init_message)
    
    def run(self):
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_UPDATE, self._on_update)

        self._init_node()

        timer = Timer()
        
        while True: 
            self.mesh.update()

    def _on_update(self, from_node, message):
        message_dict = from_json(message)

        has_succeeded = self._try_update(message_dict)

        response_dict = {'success': has_succeeded, 'id': self.id}
        confirm_message = to_json(response_dict)
        self.mesh.send_message(MeshNet.MSG_TYPE_UPDATE_CONFIRM, confirm_message)
                
    def _try_update(self, message_dict):
        if message_dict['reboot']:
            force_reboot()

        if self.functionality is not None:
            self.functionality.stop()
            del self.functionality

        if message_dict['sleep']:
            return True

        setup, loop = message_dict['setup'], message_dict['loop']

        self.functionality = Functionality(setup, loop, self.mesh)
        func_is_working = self.functionality.test()
        
        if func_is_working:
            self.functionality.start()
        
        return func_is_working


class MasterNode:
    UPDATE_INTERVAL = 10000

    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.api = Api()
        self.id = get_serial()

        self.sensor_data = {}
        self.nodes = []
        self.nodes_config = {}
        self.addresses = {}

    def _init_master(self):
        init_dict = {'nodeID': self.id, 'status': 'Online', 'isMaster': True}
        self.api.post_request('initNode', init_dict)

    def run(self):
        self._init_master()

        self.mesh.add_message_callback(MeshNet.MSG_TYPE_INIT, self._on_init)
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_UPDATE_CONFIRM, self._on_update_confirm)
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_DATA, self._on_data)

        timer = Timer()

        while True:
            self.mesh.update()

            if timer.time_passed() > MasterNode.UPDATE_INTERVAL:
                self._fetch_functionality()
                self._post_sensor_data()
                timer.reset()

    def _fetch_functionality(self): 
        try:
            updates = self.api.get_request('getFunctionality', {'email': 'jens@mytest.com'}).json() 
            # TODO: add the identification to the Api class when we figure out how to do this
            for node in updates:
                _id = node['nodeID']
                body = node['body']
                self.nodes_config[_id] = body
                self._send_update(_id)
        except Exception as e:
            print("No updates for your slaves")

    def _post_sensor_data(self):
        if self.sensor_data:
            response = self.api.post_request('updateSensorData', self.sensor_data)
            if response is not None and response.ok:
                self.sensor_data.clear()

    def _on_init(self, from_node, message):
        message_dict = from_json(message)
        self._update_address(message_dict, from_node)

        if _id in self.nodes_config: # If node already exists, just send the functionality, else init the node on server
            self._send_update(_id)
        else:
            self.nodes.append(_id)
            init_dict = {'nodeID': _id, 'status': 'Online'}
            self.api.post_request('initNode', init_dict)

        self._update_address(message_dict, from_node)

    def _on_data(self, from_node, message):
        message_dict = from_json(message)
        self._update_address(message_dict, from_node)
        
        _id = message_dict['id']
        sensor_values = message_dict['sensor-values']
        if _id  in self.sensor_data:
            self.sensor_data[_id].append(sensor_values)
        else:
            self.sensor_data[_id] = [sensor_values]

    def _on_update_confirm(self, from_node, message):
        message_dict = from_json(message)
        self._update_address(message_dict, from_node)

        update_succeeded = message_dict['success']
        # 
        # TODO: send stuff to server
        
    def _send_update(self, _id):
        status = self.nodes_config[_id]
        update_message = to_json(status)
        if _id in self.addresses:
            self.mesh.send_message(MeshNet.MSG_TYPE_UPDATE, update_message, to_address=self.addresses[_id])

    def _update_address(self, message_dict, from_node):
        if 'id' in message_dict:
            _id = message_dict['id']
            self.addresses[_id] = from_node