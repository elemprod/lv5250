

# pip3 install pyserial
import serial
import time

import arm_cmd
from arm_cmd import *

# List Serial Ports
# python -m serial.tools.list_ports

#Robot Arm Serial Port Interface Class


class ArmSerial:

    # Serial Port Defintion
    # Use python -m serial.tools.list_ports to get a list of available ports
    ARM_PORT = "/dev/cu.usbserial-FT5ZVFRV"

    def __init__(self):
        self.serial = serial.Serial()
        # Set the serial port settings but don't open the port
        self.serial.port = self.ARM_PORT
        self.serial.baudrate = 9600
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.xonxoff = False
        self.serial.rtscts = False
        self.serial.dsrdtr = False
        self.serial.exclusive = False
        self.serial.timeout = 1.0
        self.serial.write_timeout = 5.0
        self.serial.inter_byte_timeout = 0.1

    # Open the Robot Arm's Serial Port
    def open(self):
        # Close the port if its already open
        if self.serial.isOpen:
            self.serial.close()
        # Try to open the port
        try:
            self.serial.open()
        except serial.SerialException as e:
            print("Serial Port Error: " + str(e))
        else:
            print("Serial Port Opened: " + self.serial.name)
            self.serial.write(b'REMOTE\r')

    # Close the Robot Arm's Serial Port
    def close(self):
        if self.serial.isOpen:
            self.serial.close()

    def send(self, msg):
        print('Sent ' + str(self.serial.write(msg)) + " Bytes")
