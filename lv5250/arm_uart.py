import time
# pip3 install pyserial
import serial
import threading
from threading import Thread

try:
    import queue
except ImportError:
    import Queue as queue

from arm import Arm, ArmConnectionState

# Arm Message Definition - Defines an Arm Command & Response


class ArmMessage():
    def __init__(self, command, response=None, timeout=5, callback=None):
        # The command to send
        self.command = bytes(command)
        # If None, the callback will be made following any response else the
        # the callback will made after the response as received.
        if response is None:
            self.response = None
        else:
            self.response = bytes(response)
        # The maximuim time to wait in seconds
        self.timeout = float(timeout)
        # Function to call once a response has been received.
        self.callback = callback
        # The response received.
        # None if no response is received before the time out expires.
        self.received = None


class ArmUART:

    def __init__(self, port):

        # Que of responses received from the Arm via the serial link
        self.responses = queue.Queue()

        # Que of unhandled responses
        self.events = queue.Queue()

        # Lock for ensuring exclusive serial port command transmissions
        self.tx_lock = threading.Lock()

        self.serial = serial.Serial(port=port, baudrate=9600)
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.xonxoff = False
        #self.serial.rtscts = True
        #self.serial.dsrdtr = True
        self.serial.rtscts = False
        self.serial.dsrdtr = False
        self.serial.exclusive = False
        self.serial.timeout = 1.0
        self.serial.write_timeout = 5.0
        self.serial.inter_byte_timeout = 0.1
        # close the port if already open
        if self.serial.isOpen:
            self.serial.close()

        try:
            self.serial.open()
        except serial.SerialException as e:
            print("Error Openning Port: " + str(e))
        else:
            print("Port Open")
            self.reader_thread = threading.Thread(
                target=self.read_loop, daemon=True)
            self.reader_thread.start()

    # loop for adding serial messages to the responses que
    def read_loop(self):
        while self.serial.isOpen:
            line = self.serial.readline()
            #print(line)
            if len(line) > 0:
                self.responses.put(line)
            time.sleep(0.1)

    # def read_line(self):
    #     print(arm_serial.serial.readline())
    #
    # def get_pos(self):
    #     self.serial.write(bytes('GET POS\r\n', 'utf-8'))
    #
    # def hard_home(self):
    #     self.serial.write(bytes('HARDHOME\r\n', 'utf-8'))

    def send(self, message: ArmMessage):
        with self.tx_lock:
            # Send the command
            self.serial.write(message.command)
            while True:
                try:
                    line = self.responses.get(timeout=message.timeout)
                    if message.response:
                        if line == message.response:
                            # the correct response was received
                            message.received = line
                            if message.callback:
                                message.callback(message)
                            return
                        else:
                            # the received response didn't match.
                            # Save the response to the unhandled que
                            self.events.put(line)
                            # No return here, get the next line.
                            print("Unhandled" + str(line))
                    else:
                        # no response was set so return after the first response
                        message.received = line
                        if message.callback:
                            message.callback(message)
                        return
                except queue.Empty:
                    # no response was received before the timeout expired
                    if message.callback:
                        message.callback(message)
                    return


if __name__ == "__main__":

    def response_print(message: ArmMessage):
        print("Callback")
        print(message.received)

    arm_serial = ArmUART("/dev/cu.usbserial-FT5ZVFRV")

    cmd_test = ArmMessage(command=bytes('GET POS\r\n', 'utf-8'),
                          response=None, timeout=2, callback=response_print)
    while True:
        arm_serial.send(cmd_test)
        time.sleep(10)
