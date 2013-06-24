#!/usr/bin/env python
import ConfigParser
import os

import xively

from PiLiteTwitter import PiLiteBoard, poll_for_updates



class XivelyDatastream(object):
    def __init__(self, feed):
        conf = ConfigParser.ConfigParser()
        conf.read(os.path.expanduser('~/.pilite'))
        self.api = xively.XivelyAPIClient(conf.get('xively', 'apikey'))
        self.feedid = feed

    def message(self):
        feed = self.api.feeds.get(self.feedid)
        value = feed.datastreams[0].current_value
        return "%s"%value


def main():
    source = XivelyDatastream(44519)
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink)


if __name__ == "__main__":
    main()
