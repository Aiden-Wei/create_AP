#!/usr/bin/python3

import os
import hashlib
import time
#import led_flash
import re
import sys

id_file = "/boot/LobotID.txt"
pw_file = "/boot/LobotPW.txt"

def create_id():
    global id_file
    f = open(id_file, "w")
    m=hashlib.md5()
    m.update(bytes(str(time.time()), encoding='utf-8'))
    f.write(str(m.hexdigest()))
    f.close()

def create_pw():
    global pw_file
    f = open(pw_file, "w")
    f.write(str("12345678"))
    f.close()

def check_device_id():
    global id_file
    global pw_file
    
    if not os.path.exists(id_file):
        os.mknod(id_file)
        create_id()
    else:
        f = open(id_file, "r")
        try:
            alltxt = f.read()
            if len(alltxt) == 0:
                create_id()
        finally:
            f.close()
            
    if not os.path.exists(pw_file):
        os.mknod(pw_file)
        create_pw()
    else:
        f = open(pw_file, "r")
        try:
            alltxt = f.read()
            if  len(alltxt)  < 8:
                create_pw()
        finally:
            f.close() 


check_device_id()
ID = open(id_file, "r")
PW = open(pw_file, "r")
id_str = ID.read()
pw_str = PW.read()
ID.close()
PW.close()
id_str = " " + "LBT"+id_str.upper()[0:6] + " "
while True:
    if os.path.exists("/boot/wpa_supplicant.conf"):
        #led_flash.flash_delay = 6
        print("connect success")
    elif os.path.exists("/etc/wpa_supplicant/wpa_supplicant.conf"):
        os.system("sudo create_ap --stop wlan0")
        time.sleep(2)
        os.system("sudo ifconfig wlan0 up")
        os.system("sudo pkill wpa_supplicant")
        os.system("sudo pkill wpa_supplicant")
        os.system("sudo pkill wpa_supplicant")
        os.system("sudo wpa_supplicant -B -iwlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf")
        #led_flash.flash_delay = 6
        print("connect success!")
    else:
        os.system("sudo pkill ^wpa_supplicant$")
        os.system("sudo pkill ^hostapd")
        os.system("sudo systemctl stop dnsmasq.service")
        os.system("sudo ifconfig wlan0 up")
        print("creat wifi " + id_str + " success !")
        #led_flash.flash_delay = 1
        if int(sys.argv[1]) == 1:
            ap = " --freq-band 5 "
        else:
            ap = " "
        os.system("sudo create_ap --daemon --no-virt"+ap+ "-g 10.0.0.1 -n wlan0" + id_str + pw_str)
    time.sleep(2)   
    ret = os.popen("sudo ifconfig").read()
    r = re.compile(r"wlan0")
    match = r.search(ret)
    if match:
        r = re.compile(r"inet 10.0.0.1")
        match = r.search(ret)
        if match:
            break
