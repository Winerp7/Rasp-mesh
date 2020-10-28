from RF24 import *
from RF24Network import *
from RF24Mesh import *

from struct import unpack



radio = RF24(22,0) # GPIO22 for CE-pin and CE0 for CS-pin
network = RF24Network(radio)
mesh = RF24Mesh(radio, network)

mesh.setNodeID(0)
mesh.begin()
radio.setPALevel(RF24_PA_MAX) # Power Amplifier
radio.printDetails()

while True:
    mesh.update()
    mesh.DHCP()

    while network.available():
        header, payload = network.read(10)
        if chr(header.type) == 'M':
            print("Rcv {} from 0{:o}".format(unpack("L",payload)[0], header.from_node))
        else:
            print("Rcv bad type {} from 0{:o}".format(header.type,header.from_node))