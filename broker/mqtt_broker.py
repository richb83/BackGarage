#! /usr/bin/python3

import paho.mqtt.client as mqtt
import time
import json
import logging
from logging.handlers import RotatingFileHandler

verbose = False
LOG_FILENAME = '/media/pi/Samsung USB/BackGarage_Data.log'
LOG_SERVER_FILENAME = '/media/pi/Samsung USB/BackGarage.log'

# TODO  Need to add logging of mqtt messaging


def on_log(client, userdata, level, buf):
    print("log: "+buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

#  on_message will get messages from the topics subscribed to


def on_message(client, userdata, msg):
    topic = msg.topic
    msgPayload = json.loads(msg.payload)
    print("Topic: ", topic)
    print("Message: ", msgPayload)
    log_data.info("topic {a}   Message: {b}".format(a=topic, b=msgPayload))


def on_disconnect(client, userdata, flags, rc=0):
    print("Disconneted result code "+str(rc))


#  Logging setup
log = logging.getLogger(__name__)
log_data = logging.getLogger('Data_Log')
log.setLevel(logging.DEBUG)
log_data.setLevel(logging.INFO)
f_handler = RotatingFileHandler(
    LOG_SERVER_FILENAME, maxBytes=1000000, backupCount=30)
fData_handler = RotatingFileHandler(
    LOG_FILENAME, maxBytes=1000000, backupCount=30)
formater = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s ')
f_handler.setFormatter(formater)
fData_handler.setFormatter(formater)
log.addHandler(f_handler)
log_data.addHandler(fData_handler)

broker = "192.168.0.75"
client = mqtt.Client("Broker_1")

client.on_connect = on_connect
if verbose:
    client.on_log = on_log
client.on_message = on_message
client.on_disconnect = on_disconnect

print("Connecting to broker ", broker)
client.connect(broker)
# Topics
topic_con = "connection"
topic_temp = "sensor_temp"
topic_fan_ctl = "fan_ctl"
topic_fan_state = "fan_state"
topic_heater_ctl = "heater_ctl"
topic_heater_state = "heater_state"
topic_system_state = "system_state"
client.subscribe(topic_con)
client.subscribe(topic_temp)
client.subscribe(topic_fan_ctl)
client.subscribe(topic_fan_state)
client.subscribe(topic_heater_ctl)
client.subscribe(topic_heater_state)
client.subscribe(topic_system_state)
client.subscribe("topic_test")
client.loop_start()
time.sleep(10)
client.publish("topic_test", json.dumps(
    {"Broker-1": "Broker-1 connected and going in the loop"}))

while 1:
    time.sleep(30)
    client.publish("topic_test", json.dumps(
        {"broker_1": "Broker-1 in test loop 30 seconds"}))

client.loop_stop()
client.disconnect()
