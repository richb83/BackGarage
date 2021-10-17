#! /usr/bin/python3

import paho.mqtt.client as mqtt
import time
import json
import os
import re
import RPi.GPIO as GPIO

verbose = False
debug = False

# 28-01191f1acd16   Garage
# 28-011913ff09bb   Outside
# 28-01191eedd2d2   Dog House

broker = "192.168.1.101"
broker_port = 1883
basePath = '/sys/bus/w1/devices'
fname = 'w1_slave'
server = "sensor-1"

# If enabled the control can be activated
# enabled 0 = false/off   1 = true/on
fan_garage_enabled = 0
fan_dog_enabled = 0
heater_dog_enabled = 0

# if state is 1 the control is on, if 0 the control is off
# State  0 = false/off   1 = true/on
fan_garage_state = 0
fan_dog_state = 0
heater_dog_state = 0

# Topics
topic_con = "garage/connection"
topic_temp = "garage/sensor_temp"  # Depreciated
topic_temp_garage = "garage/temp/garage"
topic_temp_outside = "garage/temp/outside"
topic_temp_doghouse = "garage/temp/doghouse"
topic_fan_ctl = "garage/fan/ctl"
topic_fan_state = "garage/fan/state"
topic_heater_ctl = "garage/heater/ctl"
topic_heater_state = "garage/heater/state"
topic_system_state = "garage/system/state"
topic_fan_enabled = "garage/fan/enabled"
topic_heater_enabled = "garage/heater/enabled"

# 32 = green dog house fan   33 = garage/fan dog heater
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

# **********************************  mqtt message handling functions **************************************

# TODO  Need to add the needed message handling functions


def returnSystemState():
    fanState = {"fan_garage": fan_garage_state, "fan_dog": fan_dog_state}
    fanCtl = {"fan_dog": fan_dog_enabled}
    heaterState = {"heater_dog_state": heater_dog_state}
    heaterCtl = {"heater_dog": heater_dog_enabled}
    client.publish(topic_fan_ctl, json.dumps(fanCtl))
    client.publish(topic_fan_state, json.dumps(fanState))
    client.publish(topic_heater_ctl, json.dumps(heaterCtl))
    client.publish(topic_heater_state, json.dumps(heaterState))


def updateFanEnabled(msg):
    if (debug):
        print("In the Update Fan Enabled FUnction")

    for key, val in msg.items():
        if (debug):
            print(f"Fan Enabled key: {key} Value: {val}")
        if key == "fan_garage":
            global fan_garage_enabled
            fan_garage_enabled = int(val)
        elif key == "fan_dog":
            global fan_dog_enabled
            fan_dog_enabled = int(val)


def updateHeaterEnabled(msg):
    if (debug):
        print("In the Update Fan Enabled FUnction")

    for key, val in msg.items():
        if (debug):
            print(f"Heater Enabled key: {key} Value: {val}")
        if key == "heater_dog":
            global heater_dog_enabled
            heater_dog_enabled = int(val)


# **********************************  application functions **************************************

# TODO  Need function to control dog fan, automaticlly if enabled
# TODO  Need function to control dog heater, automaticlly if enabled
# TODO  Need function to control Garage fan, automaticlly if enabled


def checkTemps(msg):
    global fan_garage_state
    global heater_dog_state
    global fan_dog_state
    global fan_dog_enabled
    global heater_dog_enabled

    for key, val in msg.items():
        temp = int(float(val))
        if key.strip() == '28-01191eedd2d2':
            if temp >= 100:
                fan_garage_state = 1
                # TODO  turn the fan on
        elif key.strip() == '28-011913ff09bb':
            if (debug):
                print(
                    f"Check Temps sensor Match -- Fan: {fan_dog_enabled}  --  Heater: {heater_dog_enabled} ")

            # if fan_dog_enabled:
            #     fan_dog_state = 1
            # else:
            #     fan_dog_state = 0

            # if heater_dog_enabled:
            #     heater_dog_state = 1
            # else:
            #     heater_dog_state = 0

            if temp <= 40:
                if heater_dog_enabled:
                    heater_dog_state = 1
            elif temp > 45 and temp < 85:
                fan_dog_state = 0
                heater_dog_state = 0
            elif temp >= 85:
                if fan_dog_enabled:
                    fan_dog_state = 1
                else:
                    fan_dog_state = 0
    updateControls()


def updateControls():
    if (debug):
        print("In the Update Controls FUnction")

    fanCtl = {"fan_dog": fan_dog_enabled}
    heaterCtl = {"heater_dog": heater_dog_enabled}

    if (debug):
        print(f"Update Controls Fan: {fanCtl}   --  Heater: {heaterCtl}")

    if fan_dog_state:
        GPIO.output(32, GPIO.HIGH)
        ctlState = {'fan_dog': 1}
        client.publish(topic_fan_state, json.dumps(ctlState))
        client.publish(topic_fan_enabled, json.dumps(fanCtl))
    else:
        GPIO.output(32, GPIO.LOW)
        ctlState = {'fan_dog': 0}
        client.publish(topic_fan_state, json.dumps(ctlState))
        client.publish(topic_fan_enabled, json.dumps(fanCtl))

    # if fan_garage_state:
    #     GPIO.output(33, GPIO.HIGH)
    #     ctlState = {'fan_garage': 1}
    #     client.publish(topic_fan_state, json.dumps(ctlState))
    # else:
    #     GPIO.output(33, GPIO.LOW)
    #     ctlState = {'fan_garage': 0}
    #     client.publish(topic_fan_state, json.dumps(ctlState))

    if heater_dog_state:
        GPIO.output(32, GPIO.HIGH)
        ctlState = {'heater_dog': 1}
        client.publish(topic_heater_state, json.dumps(ctlState))
        client.publish(topic_heater_enabled, json.dumps(heaterCtl))
    else:
        GPIO.output(32, GPIO.LOW)
        ctlState = {'heater_dog': 0}
        client.publish(topic_heater_state, json.dumps(ctlState))
        client.publish(topic_heater_enabled, json.dumps(heaterCtl))


def get_temps():
    dictTemps = {}
    dirList = None
    if os.path.exists(basePath):
        dirList = os.listdir(basePath)
    if dirList:
        for d in dirList:
            if d != 'w1_bus_master1':
                tempData = ''
                fPath = os.path.join(basePath, d, fname)

                with open(fPath, 'r') as fo:
                    for line in fo:
                        matchObj = re.search(r't=(-*\d{2,})', line, re.I)
                        if matchObj:
                            tempData = matchObj.group(1)
                            # print('The temp is', tempData)
                        else:
                            continue
                try:
                    celsius = float(tempData) / 1000
                    farenheit = str(round((celsius * 1.8) + 32, 1))
                except:
                    continue

                dictTemps[d] = farenheit
    checkTemps(dictTemps)
    return dictTemps

# **********************************  mqtt callback functions **************************************


def on_log(client, userdata, level, buf):
    print("log: "+buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        con_data = {server: "connected"}
        sys_state = {server: 1}
        client.publish(topic_con, json.dumps(con_data))
        client.publish(topic_system_state, json.dumps(sys_state))
    else:
        con_state = "Bad connection Returned code=" + rc
        con_data = {server: "disconnected"}
        client.publish(topic_con, json.dumps(con_data))
        con_data = {server: con_state}
        client.publish(topic_con, json.dumps(con_data))

        # Connection Return Codes
        # 0: Connection successful
        # 1: Connection refused incorrect protocol version
        # 2: Connection refused invalid client identifier
        # 3: Connection refused server unavailable
        # 4: Connection refused bad username or password
        # 5: Connection refused not authorised


def on_disconnect(client, userdata, rc):
    con_state = "Bad connection Returned code=" + rc
    con_data = {server: "disconnected"}
    client.publish(topic_con, json.dumps(con_data))
    con_data = {server: ConnectionError}
    client.publish(topic_con, json.dumps(con_data))


def on_message(client, userdata, msg):
    # TODO  Need to code on_message to handle incoming control and state request messages

    topic = msg.topic
    msgPayload = json.loads(msg.payload)

    if (debug):
        print(f"In On-Message  Topic: {topic} with Payload: {msgPayload}")

    if topic == topic_system_state:
        pass
        # returnSystemState()
    elif topic == topic_fan_ctl:
        updateFanEnabled(msgPayload)
    elif topic == topic_heater_ctl:
        updateHeaterEnabled(msgPayload)


#  putting the server name in the userdata field
client = mqtt.Client(client_id="Sensor_1", clean_session=True,
                     userdata="Sensor_1")

if verbose:
    client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

con_data = {server: "disconnected"}
client.will_set(topic_con, payload=json.dumps(con_data), qos=1, retain=False)
client.connect(broker)

client.subscribe(topic_fan_ctl)
client.subscribe(topic_heater_ctl)
client.subscribe(topic_system_state)

client.loop_start()
while 1:
    time.sleep(5)
    data = get_temps()
    heaterState = {"heater_dog_state": heater_dog_state}
    client.publish(topic_heater_state, json.dumps(heaterState))
    for d in data:
        if d == '28-01191f1acd16':
            client.publish(topic_temp_garage, data[d])
        if d == '28-011913ff09bb':
            client.publish(topic_temp_outside, data[d])
        if d == '28-01191eedd2d2':
            client.publish(topic_temp_doghouse, data[d])

    #  All Sensors combined has been depreciated
    #client.publish(topic_temp, json.dumps(data))
