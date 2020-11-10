from mesh import MeshNet

from struct import unpack
import requests


def main():
    mesh = MeshNet(master=True)

    while True:
        mesh.update() # Keeps the mesh up and running and reconfigures it if need be
        
        for from_node, message in mesh.read():
            print(message, flush=True)
            r = requests.post('http://192.168.43.105:3000/api-test', data = {'id': message})
            print(r.text, flush=True)



if __name__ == '__main__':
    main()
