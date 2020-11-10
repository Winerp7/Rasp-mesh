from mesh import MeshNet
from utils import delay
from struct import *


def main():
    mesh = MeshNet(master=False)

    message = 'Hello what are you doing right now?'
    
    while True: 
        mesh.update()

        write_successful = mesh.send(message)
        if write_successful:
            print(f'Sent: {message}', flush=True)

        delay(1)
        

if __name__ == '__main__':
    main()
