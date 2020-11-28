# This Python file uses the following encoding: utf-8
from main_gui import Ui_MainWindow
from stylesheet import gui_style
from mqtt_gui import mqttClient
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
import sys
import json
import paho.mqtt.client as mqtt


class Main_Win(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.show()

# ************************** Initilaize the GUI widgets *******************************************

        self.btnFanGarage.setCheckable(True)
        self.btnFanGarage.toggled.connect(self.btnFanGarage_changed)
        self.btnFanGarage.setChecked(False)
        self.btnFanDog.setCheckable(True)
        self.btnFanDog.toggled.connect(self.btnFanDog_changed)
        self.btnFanDog.setChecked(False)
        self.btnHeatDog.setCheckable(True)
        self.btnHeatDog.toggled.connect(self.btnHeatDog_changed)
        self.btnHeatDog.setChecked(False)
        self.lblBroker_status.setStyleSheet(gui_style.lblStyleDisconnected())
        # FIXME This should have been named  lblSensor_status
        self.label.setStyleSheet(gui_style.lblStyleDisconnected())
        self.client = mqttClient()
        self.client.stateChanged.connect(self.on_stateChanged)
        self.client.tempSignal.connect(self.handleTempMessages)
        self.client.connectionSignal.connect(self.handleConnectionMessages)
        self.client.fanStateSignal.connect(self.handleFanStateMessages)
        self.client.fanControlSignal.connect(self.handleFanControlMessages)
        self.client.heatStateSignal.connect(self.handleHeatStateMessages)
        self.client.heatControlSignal.connect(self.handleHeatControlMessages)
        self.client.systemStateSignal.connect(self.handleSystemStateMessages)
        self.client.connectToBroker()


# ******************************* Fuctions handling GUI events ************************************

    def btnFanGarage_changed(self):
        # TODO  Need to code btnFanGarage_changed to send status (Enabled / Disabled) to Sensor server
        if self.btnFanGarage.isChecked():
            self.btnFanGarage.setStyleSheet(gui_style.btnStyleEnabled())
            self.btnFanGarage.setText("Garage\nFan\nEnabled")
            newState = {'fan_garage': 1}
            self.client.publish(self.client.topic_fan_ctl, newState)
        else:
            self.btnFanGarage.setStyleSheet(gui_style.btnStyleDisabled())
            self.btnFanGarage.setText("Garage\nFan\nDisabled")
            newState = {'fan_garage': 0}
            self.client.publish(self.client.topic_fan_ctl, newState)

    def btnFanDog_changed(self):
        # TODO  Need to code btnFanDog_changed to send status (Enabled / Disabled) to Sensor server
        if self.btnFanDog.isChecked():
            self.btnFanDog.setStyleSheet(gui_style.btnStyleEnabled())
            self.btnFanDog.setText("Dog\nFan\nEnabled")
            newState = {'fan_dog': 1}
            self.client.publish(self.client.topic_fan_ctl, newState)
        else:
            self.btnFanDog.setStyleSheet(gui_style.btnStyleDisabled())
            self.btnFanDog.setText("Dog\nFan\nDisabled")
            newState = {'fan_dog': 0}
            self.client.publish(self.client.topic_fan_ctl, newState)

    def btnHeatDog_changed(self):
        # TODO  Need to code btnHeatDog_changed to send status (Enabled / Disabled) to Sensor server
        if self.btnHeatDog.isChecked():
            self.btnHeatDog.setStyleSheet(gui_style.btnStyleEnabled())
            self.btnHeatDog.setText("Dog\nHeat\nEnabled")
            # TODO Add all these settings to variable file that can be added to each application
            newState = {'heater_dog': 1}
            self.client.publish(self.client.topic_heater_ctl, newState)
        else:
            self.btnHeatDog.setStyleSheet(gui_style.btnStyleDisabled())
            self.btnHeatDog.setText("Dog\nHeat\nDisabled")
            newState = {'heater_dog': 0}
            self.client.publish(self.client.topic_heater_ctl, newState)

    def updateTempGarage(self, data):
        self.pbGarage.setValue(data)

    def updateTempOutdoor(self, data):
        self.pbOutside.setValue(data)

    def updateTempDogHouse(self, data):
        self.pbDog.setValue(data)

# ******************************* Fuctions mqtt events ************************************

    @QtCore.pyqtSlot(int)
    def on_stateChanged(self, state):
        #  Status bar  name:  statusbar
        # TODO  Upon a connected status send a get system status message
        print("in state chnage function: ", str(state))
        if state == mqttClient.Connected:
            self.client.subscribe(self.client.topic_temp)
            self.client.subscribe(self.client.topic_con)
            self.client.subscribe(self.client.topic_fan_ctl)
            self.client.subscribe(self.client.topic_fan_state)
            self.client.subscribe(self.client.topic_heater_ctl)
            self.client.subscribe(self.client.topic_heater_state)
            self.client.subscribe(self.client.topic_system_state)
            # DEBUG  Subscribing to topic: topic_test - Currently on
            self.client.subscribe("topic_test")
            sys_state = {self.client.server: 1}
            self.client.publish(self.client.topic_system_state, sys_state)
            sys_state = {self.client.server: 'connected'}
            self.client.publish(self.client.topic_con, sys_state)
            self.lblBroker_status.setStyleSheet(gui_style.lblStyleConnected())

    @QtCore.pyqtSlot(object)
    def handleConnectionMessages(self, msg):
        print("Connection Message: ", msg)
        # TODO  Need to get a standard set of names for the servers
        # TODO  Need to code handleConnectionMessages  Display_1 sensor-1
        for key, val in msg.items():
            if key == "Display_1":
                if val == 'connected':
                    self.label.setStyleSheet(gui_style.lblStyleConnected())
                elif val == 'disconnected':
                    self.label.setStyleSheet(gui_style.lblStyleDisconnected())
            elif key == "sensor-1":
                if val == 'connected':
                    self.label.setStyleSheet(gui_style.lblStyleConnected())
                elif val == 'disconnected':
                    self.label.setStyleSheet(gui_style.lblStyleDisconnected())

    @QtCore.pyqtSlot(object)
    def handleTempMessages(self, msg):
        # tempSensorLocation = {"28-01191eedd2d2": "Garage", "28—011913ff09bb": "Outdoor", "28-01191f1acd16": "DogHouse"}
        print(
            "Temp message was recieved by the GUI ***************************************")
        for key, val in msg.items():
            temp = round(float(val))
            if key.strip() == '28-01191f1acd16':
                if temp <= 34:
                    self.pbGarage.setStyleSheet(gui_style.progBarStyleCold())
                elif temp <= 90:
                    self.pbGarage.setStyleSheet(gui_style.progBarStyleNormal())
                else:
                    self.pbGarage.setStyleSheet(gui_style.progBarStyleHot())
                self.pbGarage.setValue(temp)
            elif key.strip() == '28-011913ff09bb':
                if temp <= 34:
                    self.pbOutside.setStyleSheet(gui_style.progBarStyleCold())
                elif temp <= 90:
                    self.pbOutside.setStyleSheet(
                        gui_style.progBarStyleNormal())
                else:
                    self.pbOutside.setStyleSheet(gui_style.progBarStyleHot())
                self.pbOutside.setValue(temp)
            elif key.strip() == '28-01191eedd2d2':
                if temp <= 34:
                    self.pbDog.setStyleSheet(gui_style.progBarStyleCold())
                elif temp <= 90:
                    self.pbDog.setStyleSheet(gui_style.progBarStyleNormal())
                else:
                    self.pbDog.setStyleSheet(gui_style.progBarStyleHot())
                self.pbDog.setValue(temp)
            else:
                print("key did not match: ", key)

    @QtCore.pyqtSlot(object)
    def handleFanControlMessages(self, msg):

        for key, val in msg.items():
            if key == 'fan_garage':
                if val:
                    self.btnFanGarage.setChecked(True)
                else:
                    self.btnFanGarage.setChecked(False)
            if key == 'fan_dog':
                if val:
                    self.btnFanDog.setChecked(True)
                else:
                    self.btnFanDog.setChecked(False)

    @QtCore.pyqtSlot(object)
    def handleFanStateMessages(self, msg):
        for key, val in msg.items():
            if key == 'fan_garage':
                if val:
                    self.lbl_Garage_Fan_State.setStyleSheet(
                        gui_style.lblStyleConnected())
                    self.lbl_Garage_Fan_State.setText("Garage Fan\nOn")
                else:
                    self.lbl_Garage_Fan_State.setStyleSheet(
                        gui_style.lblStyleDisconnected())
                    self.lbl_Garage_Fan_State.setText("Garage Fan\nOff")
            if key == 'fan_dog':
                if val:
                    self.lbl_Dog_Fan_State.setStyleSheet(
                        gui_style.lblStyleConnected())
                    self.lbl_Dog_Fan_State.setText("Dog Fan\nOn")
                else:
                    self.lbl_Dog_Fan_State.setStyleSheet(
                        gui_style.lblStyleDisconnected())
                    self.lbl_Dog_Fan_State.setText("Dog Fan\nOff")

    @QtCore.pyqtSlot(object)
    def handleHeatControlMessages(self, msg):
        for key, val in msg.items():
            if key == 'heater_dog':
                if val:
                    self.btnHeatDog.setChecked(True)
                else:
                    self.btnHeatDog.setChecked(False)

    @QtCore.pyqtSlot(object)
    def handleHeatStateMessages(self, msg):
        for key, val in msg.items():
            if key == 'heater_dog':
                if val:
                    self.lbl_Dog_Heat_State.setStyleSheet(
                        gui_style.lblStyleConnected())
                    self.lbl_Dog_Heat_State.setText("Dog Heat\nOn")
                else:
                    self.lbl_Dog_Heat_State.setStyleSheet(
                        gui_style.lblStyleDisconnected())
                    self.lbl_Dog_Heat_State.setText("Dog Heat\nOff")

    @QtCore.pyqtSlot(object)
    def handleSystemStateMessages(self, msg):
        # TODO  Need to code handleSystemStateMessages
        pass

# ************************************** Start Program ********************************************


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_Win()
    window.show()
    sys.exit(app.exec_())
