#!/bin/sh
#
echo "Starting RPI-QL OLED Controller"
cd /home/levelkro/rpi-ql
DISPLAY=:0 sudo python3 oled.py >/home/levelkro/rpi-ql/oled.log 2>&1 &
echo "OLED Controller started"
