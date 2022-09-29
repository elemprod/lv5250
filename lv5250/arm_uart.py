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

# Arm Message Definition - Defines an Serial Arm Command & Response


class ArmMessage():
    def __init__(self, command: str, timeout=5, response: str = None, cb_done=None, cb_other=None):
        # The command to send to send.
        # Line endings are automatically added .
        self.command = '{}\r\n'.format(command)
        #print(self.command)

        # The maximuim time to wait in seconds for a matching response
        self.timeout = float(timeout)

        # The response string which is anticipated to be sent by the arm to indicate
        # that the command has completed.
        # This string can be specified as the full response string or just the starting
        # part of the response.   The done callback will be made once a matching
        # respone is received is received.
        self.response = response

        # Function to call once a matching response has been received or a timeout happens.
        self.cb_done = cb_done

        # Function to call when a respones other than the done responnse are received.
        # Other responses will be ignored if set to None
        self.cb_other = cb_other

        # Callbacks have the form of callback(message : ArmMessage, response : str)


class ArmUART:

    def __init__(self, port):

        # Que of responses received over the the serial link
        self.responses = queue.Queue()

        # Lock for ensuring exclusive Serial transmission accesss
        self.tx_lock = threading.Lock()

        # Que of messages to be sent.
        self.messages = queue.Queue()

        # Thread for reading responses over the serial port
        self.rx_thread = threading.Thread(
                target=self._rx_loop, daemon=True)

        # Thread for Writing messages to the serial port
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True)

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
            self.rx_thread.start()
            self.tx_thread.start()

    # Function for adding a message to the message que
    def message_enque(self, message: ArmMessage):
        self.messages.put(message)

    # loop for adding serial messages to the responses que
    def _rx_loop(self):
        while self.serial.isOpen:
            line = self.serial.readline()
            # Remove the line endings and leading / trailing spaces
            line = line.replace(b'\n', b'')
            line = line.replace(b'\r', b'')
            line = line.strip()
            # convert the bytes to a string
            line_str = line.decode('ascii')
            #print(line)
            if len(line_str) > 0:
                self.responses.put(line_str)
            time.sleep(0.1)

    # loop for transmitting messages from the messages que
    def _tx_loop(self):
        while self.serial.isOpen:
            try:
                message = self.messages.get(block=True, timeout=0.5)
                self.tx_message(message)
            except queue.Empty:
                time.sleep(0.1)

    # Function for sending a single message over the serial port.
    def tx_message(self, message: ArmMessage):
        with self.tx_lock:
            # Convert the command string to bytes and send
            self.serial.write(bytes(message.command, 'ascii'))
            while True:
                try:
                    line = self.responses.get(timeout=message.timeout)
                    if message.response:
                        if line.startswith(message.response):
                            # the correct response was received
                            print('Response Received')
                            if message.cb_done:
                                message.cb_done(message, line)
                            return
                        else:
                            # The response didn't match the specified response.
                            if message.cb_other:
                                message.cb_other(message, line)
                            # Don't return here, get the next line.
                    else:
                        # no response was set so return after the first response
                        if message.cb_done:
                            message.cb_done(message, line)
                        return
                except queue.Empty:
                    # no response was received before the timeout expired
                    if message.cb_done:
                        message.cb_done(message, None)
                    return


if __name__ == "__main__":

    def other_print(message: ArmMessage, response: str):
        print('Other Response : {}'.format(response))

    def get_pos_print(message: ArmMessage, response: str):
        #print('Position : {}'.format(response))
        str_arr = response.split()
        if len(str_arr) == 9:
            print('Gripper : {}'.format(str_arr[1]))
            print('Wrist Roll : {}'.format(str_arr[2]))
            print('Wrist Pitch : {}'.format(str_arr[3]))
            print('Elbow : {}'.format(str_arr[4]))
            print('Shoulder : {}'.format(str_arr[5]))
            print('Base : {}'.format(str_arr[6]))

    def hard_home_print(message: ArmMessage, response: str):
        print("Hard Home Done")

    def remote_print(message: ArmMessage, response: str):
        print('Remote : {}'.format(response))

    def run_done_print(message: ArmMessage, response: str):
        print('Run Done : {}'.format(response))

    arm_serial = ArmUART("/dev/cu.usbserial-FT5ZVFRV")

    msg_hard_home = ArmMessage(command='HARDHOME',
                               response='>END',
                               timeout=30,
                               cb_done=hard_home_print,
                               cb_other=other_print)

    msg_get_pos = ArmMessage(command='GET POS',
                             response='P',
                             timeout=2,
                             cb_done=get_pos_print,
                             cb_other=other_print)

    msg_remote = ArmMessage(command='REMOTE',
                            response=None,
                            timeout=1,
                            cb_done=remote_print,
                            cb_other=None)

    msg_remote = ArmMessage(command='REMOTE',
                            response=None,
                            timeout=1,
                            cb_done=remote_print,
                            cb_other=None)

    msg_run = ArmMessage(command='RUN 50 0 0 0 0 0 0 100 0 1',
                         response='>END',
                         timeout=1,
                         cb_done=run_done_print,
                         cb_other=other_print)

    for _ in range(1):
        #arm_serial.message_enque(msg_hard_home)
        arm_serial.message_enque(msg_get_pos)
        arm_serial.message_enque(msg_run)
        arm_serial.message_enque(msg_get_pos)
        #arm_serial.message_enque(msg_remote)

    while True:
        time.sleep(5)
