#!/bin/bash
file_sd="/boot/temporaryfiles.txt"
file_id="/etc/lobot/lobot_id"

if [ -f $file_sd ]; then
  sudo rm $file
  sudo raspi-config nonint do_expand_rootfs
  sudo chattr -i $file_id
  sudo rm $file_id
  sleep 3
  sudo reboot
fi
