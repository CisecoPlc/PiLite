#!/usr/bin/env python
"""
    LED Twitter Ticker

    This Python script fetches the latest tweet from a given twitter
    account and sends its out via serial to the MSP430.  Once the MSP430
    has finished displaying the tweet it requests that the script sends the
    next tweet to be displayed.

    Jan, 2012
    By Matt Levine

    Special thanks to:
    pySerial
    http://pyserial.sourceforge.net/
    python-twitter
    http://code.google.com/p/python-twitter/

    a .tweetrc fileshould be used to set the
    consumer_key and consumer_secret.  The file should contain the
    following five lines, replacing *consumer_key* with your consumer key, and
    *consumer_secret* with your consumer secret:

    A skeletal .tweetrc file:

        [Tweet]
        consumer_key: *consumer_key*
        consumer_secret: *consumer_password*
        access_key: *access_key*
        access_secret: *access_password*

"""

import ConfigParser
import os
from time import sleep

import twitter
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


class TwitterTimeline(object):
    def __init__(self):
        conf = ConfigParser.ConfigParser()
        conf.read(os.path.expanduser('~/.tweetrc'))
        self.api = twitter.Api(consumer_key=conf.get('Tweet', 'consumer_key'),
                               consumer_secret=conf.get('Tweet', 'consumer_secret'),
                               access_token_key=conf.get('Tweet', 'access_key'),
                               access_token_secret=conf.get('Tweet', 'access_secret'))

    def message(self):
        statuses = self.api.GetHomeTimeline(count=1)
        status = statuses[0]
	return "@%s::%s..."%(status.GetUser().GetScreenName(), status.GetText())


def poll_for_updates(source, sink, interval=60):
    oldstatus = None
    while True:
        try:
            status = source.message()
            if status != oldstatus:
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


def main():
    source = TwitterTimeline()
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink)


if __name__ == "__main__":
    main()
