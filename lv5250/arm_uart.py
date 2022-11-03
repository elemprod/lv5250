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


class ArmMessage:
    """
    Arm Message Definition
    Defines a  Arm Command & Response to send over the serial connection.
    Multiple call backs are defined so that the message can be altered prior
    to sending and the results can be processed by the higher level code.
    """

    def __init__(self, command: str, timeout=5, response: str = None, cb_start=None, cb_done=None, cb_other=None):
        # The command to send.
        # Line endings are automatically added .
        self.command = '{}\r\n'.format(command)
        #print(self.command)

        # The maximuim time to wait in seconds for a matching response before
        # timing out.
        self.timeout = float(timeout)

        # The response string which is anticipated to be received fromthe arm to indicate
        # that the command has completed.
        # This string can be specified as the full response string or just the beginning
        # part of the response.   The done callback will be made once a matching
        # respone has received or the time out happens.
        self.response = response

        # Function to call immediately before the command is sent.
        # Has the form of callback(message : ArmMessage) -> ArmMessage
        # The returned ArmMessage overwrites the existing message providing
        # an oppurtunity for the callback to update the pending message.
        self.cb_start = cb_start

        # Function to call once a matching doen response has been received or
        # a timeout happens.
        # Has the form of callback(message : ArmMessage, response : str)
        self.cb_done = cb_done

        # Function to call when a respones other than the done responnse has been received.
        # Other responses will be ignored if set to None
        # Has the form of callback(message : ArmMessage, response : str)
        self.cb_other = cb_other


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
            self.responses.queue.clear()
            self.messages.queue.clear()
            self.rx_thread.start()
            self.tx_thread.start()

    # Function for adding a message to the message que
    def tx_msg_enque(self, message: ArmMessage):
        self.messages.put(message)
        #print(self.messages.count)

    # loop for adding serial messages to the responses que
    def _rx_loop(self):
        # clear out the rx buffer before starting
        self.serial.read_all()
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
                self.tx_msg(message)
            except queue.Empty:
                time.sleep(0.1)
            except all as e:
                print(e)
        # Empty the Messages Queue on Disconnect.
        self.messages.queue.clear()

    # Function for sending a single message over the serial port.
    # Note that the function blocks.
    def tx_msg(self, message: ArmMessage):
        with self.tx_lock:
            # Make the start callback and overwrite the message with the one
            # that's returned.
            if callable(message.cb_start):
                message = message.cb_start(message)
            if message:
                # Convert the command string to bytes and send
                self.serial.write(bytes(message.command, 'ascii'))
                while True:
                    try:
                        line = self.responses.get(timeout=message.timeout)
                        if message.response:
                            if line.startswith(message.response):
                                # The correct response was received
                                #print('Response Received')
                                if callable(message.cb_done):
                                    message.cb_done(message, line)
                                return
                            else:
                                # The response didn't match the anticipated response.
                                if callable(message.cb_other):
                                    message.cb_other(message, line)
                                # Don't return here, check the next responsnes.
                        else:
                            # No anticipated response was set so return after
                            # the first response is received.
                            if callable(message.cb_done):
                                message.cb_done(message, line)
                            return
                    except queue.Empty:
                        # no response was received before the timeout expired
                        if callable(message.cb_done):
                            message.cb_done(message, None)
                        return


if __name__ == "__main__":

    def other_print(message: ArmMessage, response: str):
        print('Other Response : {}'.format(response))

    def get_pos_print(message: ArmMessage, response: str):
        #print('Position : {}'.format(response))
        if response:
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

    msg_run = ArmMessage(command='RUN 50 0 0 0 0 2500 0 -1000 0 1',
                         response='>END',
                         timeout=1,
                         cb_done=run_done_print,
                         cb_other=other_print)

    for _ in range(1):
        #arm_serial.tx_msg_enque(msg_get_pos)
        #arm_serial.tx_msg_enque(msg_run)
        #arm_serial.tx_msg_enque(msg_get_pos)
        arm_serial.tx_msg_enque(msg_remote)
        arm_serial.tx_msg_enque(msg_hard_home)
        arm_serial.tx_msg_enque(msg_get_pos)
        arm_serial.tx_msg_enque(msg_run)

    while True:
        time.sleep(5)
