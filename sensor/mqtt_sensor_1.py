#! /usr/bin/python3

import paho.mqtt.client as mqtt
import time
import json
import os
import re
import RPi.GPIO as GPIO

verbose = False
debug = True

broker = "192.168.0.75"
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
topic_con = "connection"
topic_temp = "sensor_temp"
topic_fan_ctl = "fan_ctl"
topic_fan_state = "fan_state"
topic_heater_ctl = "heater_ctl"
topic_heater_state = "heater_state"
topic_system_state = "system_state"

# 32 = green dog house fan   33 = garage/fan dog heater
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

# **********************************  mqtt message handling functions **************************************

# TODO  Need to add the needed message handling functions


def returnSystemState():
    fanState = {"fan_garage": fan_garage_state, "fan_dog": fan_dog_state}
    fanCtl = {"fan_garage": fan_garage_enabled, "fan_dog": fan_dog_enabled}
    heaterState = {"heater_dog": heater_dog_state}
    heaterCtl = {"heater_dog": heater_dog_enabled}
    client.publish(topic_fan_ctl, json.dumps(fanCtl))
    client.publish(topic_fan_state, json.dumps(fanState))
    client.publish(topic_heater_ctl, json.dumps(heaterCtl))
    client.publish(topic_heater_state, json.dumps(heaterState))


def updateFanEnabled(msg):
    for key, val in msg.items():
        if debug:
            print("UpdateFanEnabled-key: ", key)
            print("UpdateFanEnabled-val: ", val)
        if key == "fan_garage":
            global fan_garage_enabled
            fan_garage_enabled = int(val)
        elif key == "fan_dog":
            global fan_dog_enabled
            fan_dog_enabled = int(val)


def updateHeaterEnabled(msg):
    for key, val in msg.items():
        if debug:
            print("UpdateHeaterEnabled-key: ", key)
            print("UpdateHeaterEnabled-val: ", val)
        if key == "heater_dog":
            if debug:
                print("Should be updating the heater dog enabled variable")
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
    for key, val in msg.items():
        if debug:
            print('checkTemps-key: ', key)
            print('checkTemps-val: ', val)
        temp = int(float(val))
        if key.strip() == '28-01191eedd2d2':
            if temp >= 100:
                fan_garage_state = 1
                # TODO  turn the fan on
        elif key.strip() == '28-01191f1acd16':
            if temp <= 40:
                if heater_dog_enabled:
                    heater_dog_state = 1
            elif temp > 40 and temp < 85:
                fan_dog_state = 0
                heater_dog_state = 0
            elif temp >= 85:
                if fan_dog_enabled:
                    fan_dog_state = 1
    updateControls()


def updateControls():
    if debug:
        print('fan_dog_state: ', fan_dog_state)
        print('fan_garage_state: ', fan_garage_state)
        print('heater_dog_state: ', heater_dog_state)
    if fan_dog_state:
        GPIO.output(32, GPIO.HIGH)
        ctlState = {'fan_dog': 1}
        client.publish(topic_fan_state, json.dumps(ctlState))
    else:
        GPIO.output(32, GPIO.LOW)
        ctlState = {'fan_dog': 0}
        client.publish(topic_fan_state, json.dumps(ctlState))

    if fan_garage_state:
        GPIO.output(33, GPIO.HIGH)
        ctlState = {'fan_garage': 1}
        client.publish(topic_fan_state, json.dumps(ctlState))
    else:
        GPIO.output(33, GPIO.LOW)
        ctlState = {'fan_garage': 0}
        client.publish(topic_fan_state, json.dumps(ctlState))

    if heater_dog_state:
        GPIO.output(33, GPIO.HIGH)
        ctlState = {'heater_dog': 1}
        client.publish(topic_heater_state, json.dumps(ctlState))
    else:
        GPIO.output(33, GPIO.LOW)
        ctlState = {'heater_dog': 0}
        client.publish(topic_heater_state, json.dumps(ctlState))


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

                if debug:
                    print(f"Sensor: {d} Reads: {farenheit}")
                dictTemps[d] = farenheit
    checkTemps(dictTemps)
    return dictTemps

# **********************************  mqtt callback functions **************************************


def on_log(client, userdata, level, buf):
    print("log: "+buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        if debug:
            print("connected OK")
        con_data = {server: "connected"}
        sys_state = {server: 1}
        client.publish(topic_con, json.dumps(con_data))
        client.publish(topic_system_state, json.dumps(sys_state))
    else:
        con_state = "Bad connection Returned code=" + rc
        if debug:
            print(con_state)

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
    if debug:
        print(con_state)
    con_data = {server: "disconnected"}
    client.publish(topic_con, json.dumps(con_data))
    con_data = {server: ConnectionError}
    client.publish(topic_con, json.dumps(con_data))


def on_message(client, userdata, msg):
    # TODO  Need to code on_message to handle incoming control and state request messages

    topic = msg.topic
    msgPayload = json.loads(msg.payload)
    # DEBUG Print mqtt on_message - Currently on
    print("Topic: ", topic)
    print("Message: ", msgPayload)
    if topic == topic_system_state:
        returnSystemState()
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
    client.publish(topic_temp, json.dumps(data))
