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

import twitter


from PiLiteLib import PiLiteBoard, poll_for_updates


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


def main():
    source = TwitterTimeline()
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink, repeat=False)


if __name__ == "__main__":
    main()
