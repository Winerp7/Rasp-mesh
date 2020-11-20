from RF24 import *
from RF24Network import *
from RF24Mesh import *

from collections import deque
from utils import force_reboot, delay, Timer
from reedsolo import RSCodec 


MASTER_NODE_ID = 0
MAX_INIT_TRIES = 10
MAX_PAYLOAD_SIZE = 1500
MESH_DEFAULT_CHANNEL = 100
MESH_RENEWAL_TIMEOUT = 7500
CE_PIN = 22
CS_PIN = 0
BUFFER_LENGTH = 100
WRITE_INTERVAL = 100
ECC_SYMBOLS = 14

class MeshNet:
    RF24_1MBPS, RF24_2MBPS, RF24_250KBPS = range(3) # 0, 1, 2
    RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX = range(4) # 0, 1, 2, 3

    def __init__(self, master=False, data_rate=RF24_1MBPS, power_level=RF24_PA_MAX):
        self.data_rate = data_rate
        self.power_level = power_level
        self.is_master = master

        self.radio, self.network, self.mesh = self._create_mesh()
        self.error_corrector = RSCodec(ECC_SYMBOLS)
        # add a write buffer that and send messages in update

        self.write_buffer = deque(maxlen=BUFFER_LENGTH)
        self.message_callback = None
        self.timer = Timer()


    def _create_mesh(self):
        radio = RF24(CE_PIN, CS_PIN) # GPIO22 for CE-pin and CE0 for CS-pin
        network = RF24Network(radio)
        mesh = RF24Mesh(radio, network)

        if self.is_master:
            mesh.setNodeID(MASTER_NODE_ID)
        else:
            mesh.setNodeID(4)

        mesh.begin(MESH_DEFAULT_CHANNEL, rf24_datarate_e.RF24_2MBPS, MESH_RENEWAL_TIMEOUT)
        radio.setPALevel(RF24_PA_MIN) # Power Amplifier
        radio.printDetails()

        return radio, network, mesh

    def send_message(self, message, to_address=0):  # Addresses to master by default
        encoded = str.encode(message)
        encoded = self.error_corrector.encode(encoded) 
        self.write_buffer.append((encoded, to_address))

    def on_messsage(self, callback):
        self.message_callback = callback

    def update(self):
        self.mesh.update()
        if self.is_master:
            self.mesh.DHCP()

        self._read()
        if self.timer.time_passed() > WRITE_INTERVAL:
            self._write()
            self.timer.reset()

    def _read(self):
        while self.network.available():
            header, payload = self.network.read(MAX_PAYLOAD_SIZE)
            if chr(header.type) == 'M':
                message = payload.decode()
                message = self.error_corrector.decode(message)[0]
                from_node = header.from_node

                if self.message_callback is not None:
                    self.message_callback(from_node, message)

    def _write(self):
        if len(self.write_buffer) == 0:
            return

        message, to_address = self.write_buffer.pop()
        
        write_successful = self.mesh.write(to_address, message, ord('M'))

        if not write_successful:
            self.write_buffer.append((message, to_address)) # if the message fails to send put it back at start of the queue
            if not self.is_master:
                self._renewAddress()

    def _renewAddress(self):
        if not self.mesh.checkConnection():
            self.mesh.renewAddress()
