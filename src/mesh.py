from RF24 import *
from RF24Network import *
from RF24Mesh import *

from collections import deque
from utils import force_reboot, delay, Timer
from reedsolo import RSCodec 


MASTER_NODE_ID = 0
MAX_INIT_TRIES = 10
MAX_PAYLOAD_SIZE = 144
MESH_DEFAULT_CHANNEL = 100
MESH_RENEWAL_TIMEOUT = 7500
CE_PIN = 22
CS_PIN = 0
BUFFER_LENGTH = 100
WRITE_INTERVAL = 100
ECC_SYMBOLS = 14

class MeshNet:
    MSG_TYPE_INIT = 30              # ascii -> 0
    MSG_TYPE_UPDATE = 31            # ascii -> 1
    MSG_TYPE_UPDATE_CONFIRM = 32    # ascii -> 2
    MSG_TYPE_DATA = 33              # ascii -> 3

    def __init__(self, master=False):
        self.is_master = master

        self.radio, self.network, self.mesh = self._create_mesh()
        self.error_corrector = RSCodec(ECC_SYMBOLS)

        self.write_buffer = deque(maxlen=BUFFER_LENGTH)
        self.message_callbacks = {}
        self.timer = Timer()

    def _create_mesh(self):
        radio = RF24(CE_PIN, CS_PIN) # GPIO22 for CE-pin and CE0 for CS-pin
        network = RF24Network(radio)
        mesh = RF24Mesh(radio, network)

        if self.is_master:
            mesh.setNodeID(MASTER_NODE_ID)

        mesh.begin(MESH_DEFAULT_CHANNEL, rf24_datarate_e.RF24_2MBPS, MESH_RENEWAL_TIMEOUT)
        radio.setPALevel(RF24_PA_MIN) # Power Amplifier
        radio.printDetails()

        return radio, network, mesh

    def send_message(self, message_type, message, to_address=0):  # Addresses to master by default
        encoded = str.encode(message) # Convert string to byte array
        encoded = self.error_corrector.encode(encoded) # Add Error Correcting SYMBOLS
        self.write_buffer.append((message_type, encoded, to_address))

    def add_message_callback(self, message_type, callback):
        self.message_callbacks[message_type] = callback

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

            if header.type in self.message_callbacks:
                message = self.error_corrector.decode(payload)[0]  # Correct any bit flips
                message = message.decode() # Convert from byte array to string

                callback = self.message_callbacks[header.type]
                callback(header.from_node, message)

    def _write(self):
        if len(self.write_buffer) == 0:
            return

        message_type, message, to_address = self.write_buffer.pop()
        
        write_successful = self.mesh.write(to_address, message, message_type)

        if not write_successful:
            self.write_buffer.append((message_type, message, to_address)) # if the message fails to send put it in the back of the queue
            if not self.is_master:
                self._renewAddress()

    def _renewAddress(self):
        if not self.mesh.checkConnection():
            self.mesh.renewAddress()
