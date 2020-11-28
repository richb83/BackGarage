#! /usr/bin/python3

import paho.mqtt.client as mqtt
import time

verbose = False
broker = "192.168.0.3"
broker_port = 1883

def on_log(client, userdata, level, buf):
    print("log: "+buf)


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)

def on_disconnect(client, userdata, rc):
    pass

# message(msg) has "topic" "payload" "qos" "retain"
def on_message(client, userdata, msg):
    topic=msg.topic
    msgPayload=str(msg.payload)
    print("Topic: ",topic)
    print("Message: ",msgPayload)


client = mqtt.Client("Remote_1")

if verbose:
    client.on_log=on_log
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker)

client.loop_start()
client.subscribe("topic_test")
time.sleep(10)
client.publish("topic_test","Python 3 message from Remote_1")

time.sleep(20)

client.publish("topic_test", "Remote_1 about to disconnect")
time.sleep(30)

client.loop_stop()
client.disconnect()
