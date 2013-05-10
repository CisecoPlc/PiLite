#!/usr/bin/env python

from Tkinter import *
import serial


def barSet(num, value):
    s.write("$$$B{},{}\r".format(num, value))

s = serial.Serial()
s.baudrate = 9600
s.timeout = 0
s.port = "/dev/ttyAMA0"

try:
            s.open()
except serial.SerialException, e:
    sys.stderr.write("could not open port %r: %s\n" % (port, e))
    sys.exit(1)

s.write("$$$ALL,OFF\r")

root = Tk()


Scale( root, from_=100, to=0, command=lambda value: barSet(1, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(2, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(3, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(4, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(5, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(6, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(7, value)).pack(side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(8, value)).pack (side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(9, value)).pack (side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(10, value)).pack (side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(11, value)).pack (side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(12, value)).pack (side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(13, value)).pack (side=LEFT)
Scale( root, from_=100, to=0, command=lambda value: barSet(14, value)).pack (side=LEFT)

root.mainloop()