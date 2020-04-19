import paho.mqtt.client as mqtt
from PyQt5 import QtCore, QtWidgets
import json


class mqttClient(QtCore.QObject):
    Disconnected = 0
    Connecting = 1
    Connected = 2

    stateChanged = QtCore.pyqtSignal(int)
    tempSignal = QtCore.pyqtSignal(object)
    connectionSignal = QtCore.pyqtSignal(object)
    fanStateSignal = QtCore.pyqtSignal(object)
    fanControlSignal = QtCore.pyqtSignal(object)
    heatStateSignal = QtCore.pyqtSignal(object)
    heatControlSignal = QtCore.pyqtSignal(object)
    systemStateSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(mqttClient, self).__init__(parent)

        self.broker = "192.168.0.75"
        self.broker_port = 1883
        self.mqttVerbose = False
        self.server = "Display_1"
        self.debug = False
        self.con_data = {self.server: "connected"}
        self.disCon_data = {self.server: "disconnected"}

        self.m_state = mqttClient.Disconnected
        self.m_client = mqtt.Client(client_id="Display_1", clean_session=True,
                                    userdata="Display_1")

        # Topics
        self.topic_con = "connection"
        self.topic_temp = "sensor_temp"
        self.topic_fan_ctl = "fan_ctl"
        self.topic_fan_state = "fan_state"
        self.topic_heater_ctl = "heater_ctl"
        self.topic_heater_state = "heater_state"
        self.topic_system_state = "system_state"

        # DEBUG  mqtt on_log for debuging - Currently off
        #self.m_client.on_log = self.on_log
        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_disconnect = self.on_disconnect

    # ************************************ mqtt functions  **************************************************

    @QtCore.pyqtProperty(int, notify=stateChanged)
    def state(self):
        return self.m_state

    @state.setter
    def state(self, state):
        if self.m_state == state:
            return
        self.m_state = state
        self.stateChanged.emit(state)

    @QtCore.pyqtSlot()
    def connectToBroker(self):
        print("attempting to connect")
        self.m_client.connect("192.168.0.75")
        self.m_client.will_set(self.topic_con, payload=json.dumps(
            self.disCon_data), qos=1, retain=False)
        # TODO  Need to add code to handle mqttClient.Connecting state.  Look into using the status bar of the gui
        self.state = mqttClient.Connecting
        self.m_client.loop_start()

    @QtCore.pyqtSlot()
    def disconnectFromBroker(self):
        self.m_client.disconnect()

    def subscribe(self, thisTopic):
        if self.state == mqttClient.Connected:
            self.m_client.subscribe(thisTopic)

    def publish(self, thisTopic, thisData):
        if self.state == mqttClient.Connected:
            self.m_client.publish(thisTopic, json.dumps(thisData))

    # ******************************* Fuctions handling mqtt callbacks ************************************

    def on_log(self, mclient, userdata, level, buf):
        print("log: "+buf)

    def on_connect(self, mclient, userdata, flags, rc):
        print("In the on connect function")
        if rc == 0:
            self.state = mqttClient.Connected
            self.m_client.publish(self.topic_con, json.dumps(self.con_data))
        else:
            self.m_client.publish(self.topic_con, json.dumps(self.disCon_data))
            cur_data = {self.server: ConnectionError}
            self.m_client.publish(self.topic_con, json.dumps(cur_data))

            # Connection Return Codes
            # 0: Connection successful
            # 1: Connection refused incorrect protocol version
            # 2: Connection refused invalid client identifier
            # 3: Connection refused server unavailable
            # 4: Connection refused bad username or password
            # 5: Connection refused not authorised

    def on_disconnect(self, client, userdata, rc):
        con_state = "Bad connection Returned code=" + rc
        client.publish(topic_con, json.dumps(self.disCon_data))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        msgPayload = json.loads(msg.payload)
        if topic == self.topic_temp:
            # DEBUG  Print on message topic temp - Currently on
            print("Topic: ", topic)
            print("Message: ", msgPayload)
            self.tempSignal.emit(msgPayload)
        elif topic == self.topic_con:
            # DEBUG  Print on message topic connect - Currently on
            print("Topic: ", topic)
            print("Message: ", msgPayload)
            self.connectionSignal.emit(msgPayload)
        elif topic == self.topic_fan_ctl:
            self.fanControlSignal.emit(msgPayload)
        elif topic == self.topic_fan_state:
            self.fanStateSignal.emit(msgPayload)
        elif topic == self.topic_heater_ctl:
            self.heatControlSignal.emit(msgPayload)
        elif topic == self.topic_heater_state:
            self.heatStateSignal.emit(msgPayload)
        elif topic == self.topic_system_state:
            self.systemStateSignal .emit(msgPayload)
