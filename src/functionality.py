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

    def helper_functions(self): # functions available to the user
        def upload(data_dict): # TODO
            message_dict = {
                'type': 'data', 
                'sensor-values': data_dict,
                'time': datetime.now().isoformat(), # TODO MATTI CHANGE THIS TO OTHER FORMAT
                'id': get_serial()
                }
            data_message = to_json(message_dict)
            self.mesh.send_message(data_message)

        wait = lambda millis: delay(millis)
        
        return upload, wait

    def run(self):
        upload, wait = self.helper_functions()
        try:
            exec(self.setup)
            while not self.stopped:
                exec(self.loop)
        
        except Exception as e:
            self.failed = True
            print(e)

    @staticmethod
    def test_functionality(setup, loop):
        upload, wait = Functionality._test_helpers()

        success = True
        try:
            exec(setup)
            exec(loop)
        except:
            success = False
        
        return success

    @staticmethod
    def _test_helpers():
        def upload(data_dict):
            pass

        def wait(millis):
            pass

        return upload, wait
            