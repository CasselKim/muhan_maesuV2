#!bin/bash

# python part
sudo apt-get update
sudo apt-get install -y python3-pip
sudo pip3 install requests
sudo pip3 install pyupbit

# secret keys
sudo apt-get update
sudo apt-get install vim
python3 secret.py