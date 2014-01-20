#!/usr/bin/env python


import serial, time, sys


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
time.sleep(0.5)
while True:
    s.write("$$$F000000000000000000000111000011111110011111110111111111111101111111101111011000110011000110000000000000000000000000000000000000\r")
    time.sleep(0.5)
    s.write("$$$F000000000000000000000111000011111110011111110111111111111111111111111111011111110011111110000111000000000000000000000000000000\r")
    time.sleep(0.5)

