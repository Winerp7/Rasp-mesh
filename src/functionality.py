import threading
from utils import delay, get_serial, to_json
from datetime import datetime

class Functionality(threading.Thread):
    def __init__(self, setup, loop, mesh):
        super(Functionality, self).__init__()

        self.stopped = False

        self.setup = setup
        self.loop = loop
        self.mesh = mesh

    def stop(self):
        self.stopped = True

    def run(self):
        upload, wait = self._helper_functions()
        try:
            exec(self.setup)
            while not self.stopped:
                exec(self.loop)
        
        except Exception as e:
            print(e)

    def _helper_functions(self): # functions available to the user
        def upload(data_dict): # TODO
            message_dict = {
                'type': 'data', 
                'sensor-values': {**data_dict, 'time': datetime.now().isoformat()},,
                'id': get_serial()
                }
            data_message = to_json(message_dict)
            self.mesh.send_message(data_message)

        wait = lambda millis: delay(millis)
        
        return upload, wait

    def test(self):
        upload, wait = self._test_helpers()

        success = True
        try:
            exec(setup)
            exec(loop)
        except:
            success = False
        
        return success

    def _test_helpers(self):
        def upload(data_dict):
            assert isinstance(data_dict, dict)

        def wait(millis):
            assert isinstance(data_dict, int)

        return upload, wait
            