import time
# pip install pyserial (not serial)
import serial
import threading
from threading import Thread

try:
    import queue
except ImportError:
    import Queue as queue

from lv5250 import *
from lv5250.arm import *


class ArmMessage:
    """
    Arm Message Definition
    Defines a  Arm Command & Response to send over the serial connection.
    Multiple call backs are defined so that the message can be altered prior
    to sending and the results can be processed by the higher level code.
    """

    def __init__(self,
                 command: str,
                 timeout=5,
                 resp: str = None,
                 resp_ignore: str = None,
                 cb_start=None,
                 cb_done=None,
                 cb_other=None):
        """
        The command string to send. Line endings are automatically added.
        """
        self.command = '{}\r\n'.format(command)

        """
        The maximuim time to wait in seconds for a matching response before
        timing out.
        """
        self.timeout = float(timeout)

        """
        The response string which is anticipated to be received from the arm to
        indicate that the command has completed.
        This string can be specified as the full response string or just the
        beginning portion of the response.   The done callback will be made
        once a matching respone has been received or the time out happens.
        """
        self.resp = resp

        """
        The response string to ignore / discard if received.
        """
        self.resp_ignore = resp_ignore

        """
        Function to call immediately before the command is sent.
        Has the form of callback(message : ArmMessage) -> ArmMessage
        The returned ArmMessage overwrites the existing message providing
        an oppurtunity for the callback to update the pending message.
        """
        self.cb_start = cb_start

        """
        Function to call once a matching doen response has been received or
        a timeout happens.
        Has the form of callback(message : ArmMessage, response : str)
        """
        self.cb_done = cb_done

        """
        Function to call when a respones other than the done or the ignore
        responnse has been received.
        Other responses will be ignored if set to None
        Has the form of callback(message : ArmMessage, response : str)
        """
        self.cb_other = cb_other


class ArmUART:

    def __init__(self, port):

        # Que of responses received over the the serial link
        self.resps = queue.Queue()

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
            self.resps.queue.clear()
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
                self.resps.put(line_str)
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
                        line = self.resps.get(timeout=message.timeout)

                        if message.resp_ignore and line.startswith(message.resp_ignore):
                            # The Ignore response received, check the next response.
                            #print(f'Ignore Response {line} Received')
                            pass
                        elif message.resp:
                            if line.startswith(message.resp):
                                # The correct response was received
                                #print(f'Anticipated Response {line} Receieved')
                                if callable(message.cb_done):
                                    message.cb_done(message, line)
                                return
                            else:
                                # The response didn't match the anticipated
                                # response, check the next responnse.
                                if callable(message.cb_other):
                                    message.cb_other(message, line)
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
