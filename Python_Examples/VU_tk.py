#!/usr/bin/env python

from Tkinter import *
import serial
import sys

def vuSet(num, value):
    s.write("$$$V{},{}\r".format(num, value))


s = serial.Serial()
s.baudrate = 9600
s.timeout = 0 
s.port = "/dev/ttyAMA0"

try:
    s.open()
except serial.SerialException, e:
    sys.stderr.write("could not open port %r: %s\n" % (s.port, e))
    sys.exit(1)
                
s.write("$$$ALL,OFF\r")

root = Tk()

Scale( root, orient=HORIZONTAL, from_=0, to=100, length=400, command=lambda value: vuSet(1, value)).pack(anchor=CENTER)
Scale( root, orient=HORIZONTAL, from_=0, to=100, length=400, command=lambda value: vuSet(2, value)).pack(anchor=CENTER)


root.mainloop()
