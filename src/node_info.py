class NodesInfo:

    def __init__(self, _id):
        self.nodes = []
        self.sensor_data = []
        self.status = {}
        self.update_statuses = {}
        self.functionalities = {}
    
    def add_node(self, _id, status='Online', update_status='Updated'):
        self.nodes.append(_id)
        self.status[_id] = status
        self.update_statuses[_id] = update_status

    def has_functionality(self, _id):
        return _id in self.functionalities

    def set_status(self, _id, new_status):
        self.status[_id] = new_status
        # TODO: send to server

    def set_update_status(self, _id, new_update_status):
        self.update_statuses[_id] = new_update_status


    def update(self):
        # fetch func
            # if func is new, 
    

