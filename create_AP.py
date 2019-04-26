#!/usr/bin/python3

import os
import hashlib
import time
import re
import sys
import pigpio
import time
import threading

id_file = "/boot/LobotID.txt"
pw_file = "/boot/LobotPW.txt"

pi = pigpio.pi()
flash_delay = 1

def check_shutdown():#key2
    count = 0
    pi.set_mode(22, pigpio.INPUT)
    pi.set_pull_up_down(22, pigpio.PUD_UP)
    while True:
        if not pi.read(22) > 0:
            count += 1
        else:
            count = 0
        if count >= 30:
            os.system("sudo shutdown now")
        time.sleep(0.1)
            
def check_io():#key1
    global flash_delay
    global pi
    count = 0
    pi.set_mode(25, pigpio.INPUT)
    pi.set_pull_up_down(25, pigpio.PUD_UP)
    while True:
        if not pi.read(25) > 0:
            count += 1
        else:
            count = 0
        if count >= 50:
            try:
                if os.path.exists("/etc/wpa_supplicant/wpa_supplicant.conf"):
                    os.system("sudo rm /etc/wpa_supplicant/wpa_supplicant.conf")
                os.system("sudo /home/pi/create_AP/create_AP.py 0")
            except:
                pass
            flash_delay=1
            count = 0
        time.sleep(0.1)
        
def flash_led():#yellow
    global flash_delay
    global pi
    state = 0
    pi.set_mode(24, pigpio.OUTPUT)
    while True:
        if flash_delay > 5:
            pi.write(24, 0)
        elif flash_delay is 0 :
            pi.write(24, 1)
        else:
            pi.write(24, state)
            if state == 0:
                state = 1
            else:
                state = 0
        time.sleep(flash_delay)

def state_led():#bule
    global pi
    count = 0
    pi.set_mode(23, pigpio.OUTPUT)
    pi.write(23, 0)
    '''
    while True:
        if count < 1:
            pi.write(24, 0)
        else:
            pi.write(24, 1)
            if count == 20:
                count =-1 
        count += 1
        time.sleep(0.1)
    '''
    
state_led()
flash = threading.Thread(target=flash_led)
read = threading.Thread(target=check_io)
#state = threading.Thread(target=state_led)
shutdown = threading.Thread(target=check_shutdown)
read.start()
flash.start()
#state.start()
shutdown.start()

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
        flash_delay = 6
        print("connect success")
    elif os.path.exists("/etc/wpa_supplicant/wpa_supplicant.conf"):
        os.system("sudo create_ap --stop wlan0")
        time.sleep(2)
        os.system("sudo ifconfig wlan0 up")
        os.system("sudo pkill wpa_supplicant")
        os.system("sudo pkill wpa_supplicant")
        os.system("sudo pkill wpa_supplicant")
        os.system("sudo wpa_supplicant -B -iwlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf")
        flash_delay = 6
        print("connect success!")
    else:
        os.system("sudo pkill ^wpa_supplicant$")
        os.system("sudo pkill ^hostapd")
        os.system("sudo systemctl stop dnsmasq.service")
        os.system("sudo ifconfig wlan0 up")
        print("creat wifi " + id_str + " success !")
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
            flash_delay = 1
            break
