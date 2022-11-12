#!/bin/sh
#
echo "Starting RPI-QL Application"
cd /home/levelkro/rpi-ql
DISPLAY=:0 sudo python3 main.py >/home/levelkro/rpi-ql/app.log 2>&1 &
echo "Application started"
