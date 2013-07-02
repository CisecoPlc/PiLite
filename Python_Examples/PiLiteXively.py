#!/usr/bin/env python
"""
    
    a ~/.pilite file should be used to set the Xiveley API Key
    
    A skeletal .pilite file:
    
    [xively]
    apikey = *YOU_API_KEY*

"""
import ConfigParser
import os

import xively

from PiLiteLib import PiLiteBoard, poll_for_updates


class XivelyDatastream(object):
    def __init__(self, feed):
        conf = ConfigParser.ConfigParser()
        conf.read(os.path.expanduser('~/.pilite'))
        self.api = xively.XivelyAPIClient(conf.get('xively', 'apikey'))
        self.feedid = feed

    def message(self):
        feed = self.api.feeds.get(self.feedid)
        stream = feed.datastreams[0]
        return "%s %s %s %s"%(feed.title, stream.id, stream.current_value, stream.unit.label)


def main():
    source = XivelyDatastream(44519)
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink)


if __name__ == "__main__":
    main()
