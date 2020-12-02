from api import Api

class NodeInfo:
    def __init__(self):
        self.api = Api()

        self.slave_ids = []
        self.sensor_data = {}
        self.slave_functionalities = {}
        self.slave_statuses = {}
        self.slave_update_statuses = {}

        self.changed_slaves = []

    def sync(self):
        self._fetch_functionality()

        self._post_sensor_data()

        statuses = []
        for _id in self.changed_slaves:
            slave_status = self.slave_statuses[_id]
            update_status = self.slave_update_statuses[_id]
        
            status_dict = {'nodeID': _id, 'status': slave_status, 'updateStatus': update_status}
            statuses.append(status_dict)
    
        if statuses:
            self.api.post_request('updateNodes', statuses)
        
        self.changed_slaves = []

    def add_master(self, _id, status='Online'):
        init_dict = {'nodeID': _id, 'status': status, 'isMaster': True}
        self.api.post_request('initNode', init_dict)

    def add_slave(self, _id, status='Online', update_status='Pending'):
        self.slave_ids.append(_id)
        self.slave_functionalities[_id] = None
        self.slave_statuses[_id] = status
        self.slave_update_statuses[_id] = update_status
        self.sensor_data[_id] = []
        
        self._notify_status_change(_id)

        init_dict = {'nodeID': _id, 'status': status}
        self.api.post_request('initNode', init_dict)
        
    def slave_exists(self, _id):
        return _id in self.slave_ids

    def set_status(self, _id, status):
        if _id in self.slave_ids:
            self.slave_statuses[_id] = status
            self._notify_status_change(_id)

    def set_update_status(self, _id, update_status):
        if _id in self.slave_ids:
            self.slave_update_statuses[_id] = update_status
            self._notify_status_change(_id)
    
    def add_data(self, _id, data):
        if _id in self.slave_ids:
            self.sensor_data[_id].append(data)

    def _notify_status_change(self, _id):
        self.changed_slaves.append(_id)

    def get_pending_functionalities(self):
        pending_funcs = []
        for _id in self.slave_ids:
            if self.slave_update_statuses[_id] == 'Pending':
                func = self.slave_functionalities[_id]
                if func is not None:
                    pending_funcs.append((_id, func))

        return pending_funcs

    def _fetch_functionality(self): 
        try:
            updates = self.api.get_request('getFunctionality').json() 
            for node in updates:
                _id = node['nodeID']
                body = node['body']
                if _id not in self.slave_ids or self.slave_functionalities[_id] != body:  # if the functionality is new
                    self.slave_functionalities[_id] = body
                    self.slave_update_statuses[_id] = 'Pending'
        except Exception as e:
            print("No updates for your slaves", flush=True)

    def _post_sensor_data(self):
        if self.sensor_data:
            response = self.api.post_request('updateSensorData', self.sensor_data)
            if response is not None and response.ok:
                for key in self.sensor_data:
                    self.sensor_data[key] = []

    