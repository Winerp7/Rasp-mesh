from api import Api

class SlaveInfo:
    def __init__(self):
        self.api = Api()

        self.slave_ids = []
        self.sensor_data = {}
        self.slave_functionalities = {}
        self.slave_statuses = {}
        self.slave_update_statuses = {}

        self.changed_slaves = []

    def sync(self):
        for _id in self.changed_slaves:
            pass
    
        # upload the stuff to the server
        # fetch functionality

        self.changed_slaves = []

    def add_slave(self, _id, status='Online', update_status='Pending'):
        self.slave_ids.append(_id)
        self.slave_functionalities[_id] = None
        self.slave_statuses[_id] = status
        self.slave_update_statuses[_id] = update_status
        self.sensor_data[_id] = []
        
        self._notify_change(_id)

        init_dict = {'nodeID': _id, 'status': status}
        self.api.post_request('initNode', init_dict)
        
    def slave_exists(self, _id):
        return _id in self.slave_ids

    def get_functionality(self, _id):
        return self.slave_functionalities[_id]

    def set_status(self, _id, status):
        if _id in self.slave_ids:
            self.slave_statuses[_id] = status
            self._notify_change(_id)

    def set_update_status(self, _id, update_status):
        if _id in self.slave_ids:
            self.slave_update_statuses[_id] = update_status
            self._notify_change(_id)
    
    def add_data(self, _id, data):
        if _id in self.slave_ids:
            self.sensor_data[_id].append(data)
            self._notify_change(_id)

    def _notify_change(self, _id):
        self.changed_slaves.append(_id)

    def _fetch_functionality(self): 
        try:
            updates = self.api.get_request('getFunctionality').json() 
            for node in updates:
                _id = node['nodeID']
                body = node['body']
                if _id not in self.node_functionalities or self.node_functionalities[_id] != body:  # if the functionality is new
                    self.node_functionalities[_id] = body
                    self.node_update_statuses[_id] = 'Pending'

                if self.node_update_statuses[_id] == 'Pending':  # if it's new or the slave has yet to update
                    self._update_slave(_id)

        except Exception as e:
            print("No updates for your slaves", flush=True)

    