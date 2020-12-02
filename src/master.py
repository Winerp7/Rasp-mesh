from mesh import MeshNet
from utils import get_serial, delay, Timer, from_json_string, to_json_string, force_reboot
from api import Api
from node_info import NodeInfo

class MasterNode:
    UPDATE_INTERVAL = 10000
    LOOP_DELAY = 0

    def __init__(self):
        self.mesh = MeshNet(master=True)
        self.api = Api()
        self.id = get_serial()
        self.node_addresses = {}

        self.node_info = NodeInfo()

    def run(self):
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_INIT, self._on_init)
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_UPDATE_CONFIRM, self._on_update_confirm)
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_DATA, self._on_data)

        self.node_info.add_master(self.id)

        timer = Timer()
        while True:
            self.mesh.update()

            if timer.time_passed() > MasterNode.UPDATE_INTERVAL:
                self._check_slave_statuses()
                self.node_info.sync()  # upload data and fetch new functionalities
                self._update_slaves()  # push new functionality to the slaves
                timer.reset()

            delay(MasterNode.LOOP_DELAY)

    def _on_init(self, from_node, message):
        message_dict = from_json_string(message)   # TODO: move to mesh.py
        self._update_address(message_dict, from_node)
        _id = message_dict['id']

        if self.node_info.slave_exists(_id):
            self.node_info.set_update_status(_id, 'Pending')  # Set it to pending so it will get the functionality
        else:
            self.node_info.add_slave(_id)

        self._update_address(message_dict, from_node)

    def _on_data(self, from_node, message):
        message_dict = from_json_string(message)
        self._update_address(message_dict, from_node)

        _id = message_dict['id']
        sensor_values = message_dict['sensor-values']
        self.node_info.add_data(_id, sensor_values)

    def _on_update_confirm(self, from_node, message):
        message_dict = from_json_string(message)
        self._update_address(message_dict, from_node)

        update_succeeded = message_dict['success']
        _id = message_dict['id']

        update_status = 'Updated' if update_succeeded else 'Failed' # TODO: make these constants in the slave_info file
        self.node_info.set_update_status(_id, update_status)
        
    def _update_slaves(self):
        for _id, func in self.node_info.get_pending_functionalities():
            update_message = to_json_string(func)
            if _id in self.node_addresses:
                self.mesh.send_message(MeshNet.MSG_TYPE_UPDATE, update_message, to_address=self.node_addresses[_id])
            
    def _update_address(self, message_dict, from_node): #TODO: move addresses into mesh.py
        _id = message_dict['id']
        self.node_addresses[_id] = from_node

    def _check_slave_statuses(self): # TODO: move some of this into mesh.py
        for _id, address in self.node_addresses.items():
            alive = self.mesh.ping(address)

            node_status = 'Online' if alive else 'Offline'
            self.node_info.set_status(_id, node_status)
            
