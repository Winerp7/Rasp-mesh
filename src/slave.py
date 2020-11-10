from mesh import MeshNet
from utils import delay
from struct import *
from time import time

start = time()

def millis():
    return int((time()-start)*1000) % (2 ** 32)


def main():
    mesh = MeshNet(master=False)

    message = 'Hello this string is not too big'
    displayTimer = millis()
    
    while True: 
        mesh.update()

        if (millis() - displayTimer) >= 1000:
            displayTimer = millis()

            write_successful = mesh.send(message)
            if write_successful:
                print(f'Sent: {message}', flush=True)

        delay(1)
        

if __name__ == '__main__':
    main()
