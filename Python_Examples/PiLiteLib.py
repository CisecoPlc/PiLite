from collections import deque
from time import sleep

import requests
import serial


class PiLiteBoard(object):
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)
        self.ser.write("$$$SPEED50\r")

    def write(self, text):
        text = text.encode('utf-8')
        while text:
            self.ser.write(text[:14])
            text = text[14:]
            sleep(3)


def poll_for_updates(source, sink, interval=60, repeat=True):
    oldstatus = None
    while True:
        try:
            status = source.message()
            if repeat or status != oldstatus:
                print(status)
                oldstatus = status
                sink.write(status)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print("Error:" + str(e))
            sink.write("...oops...error...")
            sink.write(str(e))
        sleep(interval)


class JSONPoll(object):
    def __init__(self, url, message_format, params=None):
        self.url = url
        self.message_format = message_format
        self.params = params or {}

    def message(self):
        data = requests.get(self.url, params=self.params).json()
        return self.message_format.format(**self.mung_data(data))

    def mung_data(self, data):
        return data


class CyclingSources(object):
    def __init__(self, *sources):
        self.sources = deque(sources)

    def message(self):
        message = self.sources[0].message()
        self.sources.rotate(-1)
        return message

    def __len__(self):
        return len(self.sources)
