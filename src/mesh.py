from RF24 import *
from RF24Network import *
from RF24Mesh import *

from collections import deque
from utils import force_reboot, delay, Timer


MASTER_NODE_ID = 0
MAX_INIT_TRIES = 10
MAX_PAYLOAD_SIZE = 10
MESH_DEFAULT_CHANNEL = 97
MESH_RENEWAL_TIMEOUT = 7500
CE_PIN = 22
CS_PIN = 0
BUFFER_LENGTH = 100
WRITE_INTERVAL = 100


class MeshNet:
    RF24_1MBPS, RF24_2MBPS, RF24_250KBPS = range(3) # 0, 1, 2
    RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX = range(4) # 0, 1, 2, 3

    def __init__(self, master=False, data_rate=RF24_1MBPS, power_level=RF24_PA_MAX):
        self.data_rate = data_rate
        self.power_level = power_level
        self.is_master = master

        self.radio, self.network, self.mesh = self._force_init()

        self.radio.setPALevel(self.power_level)
        self.radio.printDetails()
        # add a write buffer that and send messages in update

        self.write_buffer = deque(maxlen=BUFFER_LENGTH)
        self.message_callback = None
        self.timer = Timer()


    def send_message(self, message):
        encoded = str.encode(message)
        self.write_buffer.append(encoded)

    def on_messsage(self, callback):
        self.message_callback = callback

    def update(self):
        self.mesh.update()
        if self.is_master:
            self.mesh.DHCP()

        if self.is_master:
            self._read()
        else:
            if self.timer.time_passed() > WRITE_INTERVAL:
                self._write()
                self.timer.reset()

    def _read(self):
        while self.network.available():
            header, payload = self.network.read(MAX_PAYLOAD_SIZE)
            if chr(header.type) == 'M':
                message = payload.decode()
                from_node = header.from_node
                print(message)
                
                if self.message_callback is not None:
                    self.message_callback(from_node, message)

    def _write(self):
        if len(self.write_buffer) == 0:
            return

        message = self.write_buffer[0]
        
        write_successful = self.mesh.write(message, ord('M'))
        if write_successful: # If it sends the message we delete it from the buffer
            self.write_buffer.pop()
        else:
            self._renewAddress()

    def _force_init(self):
        
        try:
            self.radio = RF24(CE_PIN, CS_PIN) # GPIO22 for CE-pin and CE0 for CS-pin
            self.network = RF24Network(self.radio)
            self.mesh = RF24Mesh(self.radio, self.network)

            #if self.is_master:
            self.mesh.setNodeID(MASTER_NODE_ID if self.is_master else 4)
            
            self.mesh.begin()

        except Exception as e:
            print('INIT FAILED', e, flush=True)


        print('REBOOTING', flush=True)
        #force_reboot()

    def _renewAddress(self):
        if not self.mesh.checkConnection():
            self.mesh.renewAddress()
