from RF24 import *
from RF24Network import *
from RF24Mesh import *

from collections import deque
from utils import force_reboot

MASTER_NODE_ID = 0
MAX_INIT_TRIES = 10
MAX_PAYLOAD_SIZE = 1500
MESH_DEFAULT_CHANNEL = 97
MESH_RENEWAL_TIMEOUT = 7500
CE_PIN = 22
CS_PIN = 0


class MeshNet:
    RF24_1MBPS, RF24_2MBPS, RF24_250KBPS = range(3) # 0, 1, 2
    RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX = range(4) # 0, 1, 2, 3

    def __init__(self, master=False, data_rate=RF24_1MBPS, power_level=RF24_PA_MAX):
        self.data_rate = data_rate
        self.power_level = power_level
        self.is_master = master

        self.radio, self.network, self.mesh = self.force_init()

        self.radio.setPALevel(self.power_level)
        self.radio.printDetails()

    def force_init(self):
        done = False
        
        for i in range(MAX_INIT_TRIES):
            try:
                radio = RF24(CE_PIN, CS_PIN) # GPIO22 for CE-pin and CE0 for CS-pin
                network = RF24Network(radio)
                mesh = RF24Mesh(radio, network)

                if self.is_master:
                    mesh.setNodeID(MASTER_NODE_ID)

                mesh.begin()
                
                return radio, network, mesh

            except Exception as e:
                print('INIT FAILED', e, flush=True)
                if i < MAX_INIT_TRIES - 1:
                    print('RETRYING', flush=True)

        print('REBOOTING', flush=True)
        #force_reboot()

    def send(self, message):
        assert isinstance(message, str) # Make sure the message is a string
        message = str.encode(message)

        write_successful = self.mesh.write(message, ord('M'))
        if not write_successful:
            self.renewAddress()
        
        return write_successful


    def read(self):
        messages = []

        while self.network.available():
            header, payload = self.network.read(MAX_PAYLOAD_SIZE)
            if chr(header.type) == 'M':
                message = payload.decode('utf-8')
                from_node = header.from_node
                messages.append((from_node, message))
        
        return messages

    def update(self):
        self.mesh.update()
        if self.is_master:
            self.mesh.DHCP()

    def renewAddress(self):
        if not self.mesh.checkConnection():
            self.mesh.renewAddress()