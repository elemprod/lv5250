
import tkinter
from tkinter import *
from tkinter import Button

import lv5250
from lv5250 import *
from lv5250.axis import *
from lv5250.arm_manager import *
from lv5250.axises import *
from lv5250.arm import *

import serial
import serial.tools.list_ports


class ArmPort():

    def test_cb(self):
        print("test press")
        selected = self.port_lb.curselection()
        print(selected)
        if selected != None:
            port = self.ports[selected[0]].device
            print(f'Port:{port}')

    def __init__(self):
        super().__init__()

        self.top = Tk()
        self.top.title("LV5250 Port Selection")
        self.top.geometry("500x200")

        self.port_lb = Listbox(top)
        self.port_lb.grid(row=1, column=1, padx=10, pady=10)

        test_but = Button(top, text='Test Port', command=self.test_cb)
        test_but.grid(row=1, column=2)

        self.ports = serial.tools.list_ports.comports()
        self.port_lb.width = port_lb_width(self.ports)

        for index in range(len(self.ports)):
            self.port_lb.insert((index + 1), self.ports[index].device)
        top.mainloop()

    def port_lb_width(self, ports) -> int:
        '''
        Sets the ports list box width to the length of the longest name
        of a ports list with a minimuim of 20.
        '''
        width = 20
        for port in ports:
            if len(port.name) > width:
                width = len(port.name)
        self.port_lb.width = width

    def ports_lb_update(self, ports):
        '''
        Update the Ports List Box
        '''

        max_length = 10
        for port in self.ports:
            if len(port.device) > max_length:
                max_length = len(port.device)
        self.port_lb.width = max_length

        for index in range(len(self.ports)):
            self.port_lb.insert((index + 1), self.ports[index].device)


if __name__ == "__main__":
    arm_port = ArmPort()
