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
time.sleep(0.2)

# fill top VU from left to right
for v in range(0,100):
    s.write("$$$V1,{}\r".format(v))
    time.sleep(0.01)
# empty top VU
for v in range(0,100):
    s.write("$$$V1,{}\r".format(100-v))
    time.sleep(0.01)
# fill bottom vu
for v in range(0,100):
    s.write("$$$V2,{}\r".format(v))
    time.sleep(0.01)
# fill top and empty bottom at the same time
for v in range(0,100):
    s.write("$$$V1,{}\r".format(v))
    s.write("$$$V2,{}\r".format(100-v))
    #time.sleep(0.01)
# empty top vu
for v in range(0,100):
    s.write("$$$V1,{}\r".format(100-v))
    time.sleep(0.01)

time.sleep(0.2)
s.write("$$$ALL,OFF\r")
