#!/usr/bin/env python
from collections import deque

import arrow

from PiLiteTwitter import PiLiteBoard, poll_for_updates


class WorldTime(object):
    def __init__(self, label, timezone):
        self.label = label
        self.timezone = timezone

    def message(self):
       now = arrow.utcnow().to(self.timezone)
       return "{} : {}".format(self.label, now.format("HH:mm:ss"))


class CyclingSources(object):
    def __init__(self, *sources):
        self.sources = deque(sources)

    def message(self):
        message = self.sources[0].message()
        self.sources.rotate(-1)
        return message

    def __len__(self):
        return len(self.sources)

        
def main():
    source = CyclingSources(WorldTime("London", "Europe/London"),
               WorldTime("Cairo", "Africa/Cairo"),
               WorldTime("Paris", "Europe/Paris"))
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink, 60/len(source))


if __name__ == "__main__":
    main()
