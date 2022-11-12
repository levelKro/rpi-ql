#!/bin/sh
#
echo "Starting RPI-QL Application and Web server"
cd /home/levelkro/rpi-ql
./start-web.sh
./start-gui.sh
echo "Application and Web server started"
