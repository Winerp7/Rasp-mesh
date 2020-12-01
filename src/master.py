from mesh import MeshNet
from utils import get_serial, delay, Timer, from_json, to_json, force_reboot
from api import Api


class MasterNode:
    UPDATE_INTERVAL = 10000

    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.api = Api()
        self.id = get_serial()

        self.sensor_data = {}

        self.node_functionalities = {}
        self.node_addresses = {}
        self.node_update_statuses = {}

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
                self._check_node_status()
                self._post_sensor_data()
                timer.reset()

    def _fetch_functionality(self): 
        try:
            updates = self.api.get_request('getFunctionality').json() 
            # TODO: add the identification to the Api class when we figure out how to do this
            for node in updates:
                _id = node['nodeID']
                body = node['body']
                if _id not in self.node_functionalities or self.node_functionalities[_id] != body:  # if the functionality is new
                    self.node_functionalities[_id] = body
                    self.node_update_statuses[_id] = 'Pending'

                if self.node_update_statuses[_id] == 'Pending':  # if it's new or the slave has yet to update
                    self._send_update(_id)

        except Exception as e:
            print("No updates for your slaves", flush=True)

    def _post_sensor_data(self):
        if self.sensor_data:
            response = self.api.post_request('updateSensorData', self.sensor_data)
            if response is not None and response.ok:
                self.sensor_data.clear()

    def _on_init(self, from_node, message):
        message_dict = from_json(message)
        self._update_address(message_dict, from_node)

        _id = message_dict['id']
        if _id in self.node_functionalities: # If node already exists, just send the functionality, else init the node on server
            self._send_update(_id)
            self.node_update_statuses[_id] = 'Updated'
        else:
            self.node_update_statuses[_id] = 'Pending'
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
        _id = message_dict['id']
        self.node_update_statuses[_id] = 'Updated' if update_succeeded else 'Failed'
        
    def _send_update(self, _id):
        status = self.node_functionalities[_id]
        update_message = to_json(status)
        if _id in self.node_addresses:
            self.mesh.send_message(MeshNet.MSG_TYPE_UPDATE, update_message, to_address=self.node_addresses[_id])

    def _update_address(self, message_dict, from_node):
        _id = message_dict['id']
        self.node_addresses[_id] = from_node

    def _check_node_status(self):
        status = []

        for _id, address in self.node_addresses.items():
            alive = self.mesh.ping(address)

            node_status = 'Online' if alive else 'Offline'
            update_status = self.node_update_statuses[_id]
            status_dict = {'nodeID': _id, 'status': node_status, 'updateStatus': update_status}

            status.append(status_dict)
            

        if status:
            self.api.post_request('updateNodes', status)
            
