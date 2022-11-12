#!/bin/sh
#
echo "Updating system"
sudo apt -qq update -y  >/home/levelkro/rpi-ql/update.log 2>&1
echo "Upgrading system"
sudo apt -qq upgrade -y  >/home/levelkro/rpi-ql/update.log 2>&1
rm /home/levelkro/rpi-ql/update.log
