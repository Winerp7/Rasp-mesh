from RF24 import *
from RF24Network import *
from RF24Mesh import *

from struct import unpack
import requests


def main():
    radio = RF24(22,0) # GPIO22 for CE-pin and CE0 for CS-pin
    network = RF24Network(radio)
    mesh = RF24Mesh(radio, network)

    mesh.setNodeID(0)
    mesh.begin()
    radio.setPALevel(RF24_PA_MAX) # Power Amplifier
    radio.printDetails()

    while True:
        mesh.update() # Keeps the mesh up and running and reconfigures it if need be
        mesh.DHCP() # Handles address requests from the slaves
        
        # While there are message available
        while network.available():
            header, payload = network.read(10)
            if chr(header.type) == 'M':
                message = payload.decode('utf-8')
                print(message)
                from_node = header.from_node
                r = requests.post('http://192.168.43.105:3000/api-test', data = {'id': message})
                print(r.text)
            else:
                print("Rcv bad type {} from 0{:o}".format(header.type,header.from_node))


if __name__ == '__main__':
    main()
