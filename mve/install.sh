# install script for azure ubuntu 20.04
sudo sed -i 's/main restricted/main universe/g' /etc/apt/sources.list
sudo apt update
sudo apt install wget git screen openjdk-11-jre-headless python3 python3-pip unzip lrzsz -y
pip3 install psutil
