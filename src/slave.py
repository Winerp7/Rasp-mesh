from RF24 import *
from RF24Network import *
from RF24Mesh import *

from utils import delay, getserial

from struct import pack


def main():
    radio = RF24(22,0) # GPIO22 for CE-pin and CE0 for CS-pin
    network = RF24Network(radio)
    mesh = RF24Mesh(radio, network)
    
    mesh.setNodeID(1)
    print("start nodeID", mesh.getNodeID())
    mesh.begin()
    radio.setPALevel(RF24_PA_MAX) # Power Amplifier
    radio.printDetails()

    message = int(getserial(), 16)

    while True: 

        mesh.update()

        write_succesful = mesh.write(pack("L", message), ord('M'))

        if not write_succesful:

            if not mesh.checkConnection():
                print("Renewing Address")
                mesh.renewAddress()

            else:
                print("Send fail, Test OK")

        else:
            print("Send OK:", message_index)

   
        delay(1000)
    

if __name__ == '__main__':
    main()
