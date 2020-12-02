from mesh import MeshNet
from utils import get_serial, delay, Timer, from_json_string, to_json_string, force_reboot
from functionality import Functionality

class SlaveNode:
    LOOP_DELAY = 10

    def __init__(self):
        self.mesh = MeshNet(master=False)
        self.id = get_serial()
        self.functionality = None

    def _init_node(self):
        message_dict = {'id': self.id}
        init_message = to_json_string(message_dict)
        self.mesh.send_message(MeshNet.MSG_TYPE_INIT, init_message)
    
    def run(self):
        self.mesh.add_message_callback(MeshNet.MSG_TYPE_UPDATE, self._on_update)

        self._init_node()

        timer = Timer()
        
        while True: 
            self.mesh.update()
            delay(SlaveNode.LOOP_DELAY)

    def _on_update(self, from_node, message):
        message_dict = from_json_string(message)

        has_succeeded = self._try_update(message_dict)

        response_dict = {'success': has_succeeded, 'id': self.id}
        confirm_message = to_json_string(response_dict)
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

