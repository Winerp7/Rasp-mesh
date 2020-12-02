from RF24 import *
from RF24Network import *
from RF24Mesh import *

from collections import deque
from utils import force_reboot, delay, Timer, delete_dhcplist
from reedsolo import RSCodec 

MASTER_NODE_ID = 0
MAX_INIT_TRIES = 10
MAX_PAYLOAD_SIZE = 144
MESH_DEFAULT_CHANNEL = 100
MESH_RENEWAL_TIMEOUT = 7500
CE_PIN = 22
CS_PIN = 0
BUFFER_LENGTH = 100
WRITE_INTERVAL = 500
ECC_SYMBOLS = 14
MAX_MESSAGE_SIZE = MAX_PAYLOAD_SIZE - ECC_SYMBOLS - 10

class MeshNet:
    MSG_TYPE_INIT = 30              # ascii -> 0
    MSG_TYPE_UPDATE = 31            # ascii -> 1
    MSG_TYPE_UPDATE_CONFIRM = 32    # ascii -> 2
    MSG_TYPE_DATA = 33              # ascii -> 3

    MSG_TYPE_MULTI = 34             # ascii -> 4
    MSG_TYPE_PING = 35              # ascii -> 5

    def __init__(self, master=False):
        if master:
            delete_dhcplist()

        self.is_master = master

        self.radio, self.network, self.mesh = self._create_mesh()
        self.error_corrector = RSCodec(ECC_SYMBOLS)

        self.write_buffer = deque(maxlen=BUFFER_LENGTH)
        self.read_buffer = {}
        self.message_callbacks = {}
        self.write_timer = Timer()

    def _create_mesh(self):
        radio = RF24(CE_PIN, CS_PIN)
        network = RF24Network(radio)
        mesh = RF24Mesh(radio, network)

        if self.is_master:
            mesh.setNodeID(MASTER_NODE_ID)

        for _ in range(MAX_INIT_TRIES):
            succes = mesh.begin(MESH_DEFAULT_CHANNEL, rf24_datarate_e.RF24_2MBPS, MESH_RENEWAL_TIMEOUT)
            if succes:
                break

        radio.setPALevel(RF24_PA_MIN) # Power Amplifier
        radio.printDetails()

        return radio, network, mesh

    def send_message(self, message_type, message, to_address=0):  # Addresses to master by default
        print("Send:", message, flush=True)
        encoded = str.encode(message) # Convert string to byte array
        self.write_buffer.append((message_type, encoded, to_address))

    def add_message_callback(self, message_type, callback):
        self.message_callbacks[message_type] = callback

    def ping(self, to_address):
        return self.mesh.write(to_address, b'', MeshNet.MSG_TYPE_PING)

    def update(self):
        self.mesh.update()
        if self.is_master:
            self.mesh.DHCP()

        self._read()
        if self.write_timer.time_passed() > WRITE_INTERVAL:
            self._write()
            self.write_timer.reset()

    def _read(self):
        while self.network.available():
            self.write_timer.reset() # reset write interval time, so it doesnt write just after reading, since this causes errors

            header, payload = self.network.read(MAX_PAYLOAD_SIZE)
            try:
                message = self.error_corrector.decode(payload)[0]  # Correct any bit flips
                message = message.decode() # Convert from byte array to string
            except Exception as e:
                print(type(e), e.args, e, flush=True)
                return

            if header.type == MeshNet.MSG_TYPE_MULTI:
                if header.from_node in self.read_buffer:
                    self.read_buffer[header.from_node].append(message)
                else:
                    self.read_buffer[header.from_node] = [message]
            
            elif header.type in self.message_callbacks:
                if header.from_node in self.read_buffer:
                    message = "".join(self.read_buffer[header.from_node]) + message
                    del self.read_buffer[header.from_node]
                
                print("Received:", message, flush=True)
                if header.type in self.message_callbacks:
                    callback = self.message_callbacks[header.type]
                    try:
                        callback(header.from_node, message)
                    except Exception as e:
                        print('callback func failed', flush=True)
                        print(type(e), e.args, e, flush=True)

    def _write(self):
        if len(self.write_buffer) == 0:
            return

        message_type, message, to_address = self.write_buffer.pop()

        if len(message) > MAX_MESSAGE_SIZE:
            write_successful = self._multi_message_write(to_address, message, message_type)
        else: 
            ecc_message = self.error_corrector.encode(message) # Add Error Correcting SYMBOLS
            write_successful = self.mesh.write(to_address, ecc_message, message_type)

        if not write_successful:
            self.write_buffer.append((message_type, message, to_address)) # if the message fails to send put it in the back of the queue
            if not self.is_master:
                self._renewAddress()

    def _multi_message_write(self, to_address, message, message_type):
        chunks = [message[i:i+MAX_MESSAGE_SIZE] for i in range(0, len(message), MAX_MESSAGE_SIZE)] # split message in to chunks
        
        for chunk in chunks[:-1]: # loop through all chunks except for the last one
            chunk = self.error_corrector.encode(chunk)
            write_successful = self.mesh.write(to_address, chunk, MeshNet.MSG_TYPE_MULTI)
            if not write_successful:
                return False

            delay(WRITE_INTERVAL)

        chunk = self.error_corrector.encode(chunks[-1])
        return self.mesh.write(to_address, chunk, message_type)

    def _renewAddress(self):
        if not self.mesh.checkConnection():
            self.mesh.renewAddress()
