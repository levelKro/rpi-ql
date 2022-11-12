#!/bin/sh
#
echo "Starting RPI-QL Web server"
cd /home/levelkro/rpi-ql
DISPLAY=:0 sudo python3 web.py >/home/levelkro/rpi-ql/web.log 2>&1 &
echo "Web server started"
