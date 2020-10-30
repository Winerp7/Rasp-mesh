#!/bin/bash
sudo apt-get install python3-pip python3-dev libboost-python-dev python3-setuptools python3-rpi.gpio
wget http://tmrh20.github.io/RF24Installer/RPi/install.sh
chmod +x install.sh
./install.sh
cd rf24libs/RF24/pyRF24
sudo python3 setup.py build
sudo python3 setup.py install
cd pyRF24Network
sudo python3 setup.py install
cd ..
cd pyRF24Mesh
sudo python3 setup.py install
cd

