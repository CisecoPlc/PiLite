#!/usr/bin/env python
import urllib

from PiLiteLib import PiLiteBoard, poll_for_updates, JSONPoll


class StockPoll(JSONPoll):
    def __init__(self, stock, message_format=""):
        """ Encoding a space in the url a + breaks YQL, so requests params
            handling can't be used
        """
        default_format = "{symbol} {Bid},{PercentChange}"
    base_url = "http://query.yahooapis.com/v1/public/yql"
        querystring = "from yahoo.finance.quotes where symbol='%s'"
        fmt = "format=json"
        env = "env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
        url = "%s?q=select%%20*%%20%s&%s&%s"%(base_url, urllib.quote(querystring%stock), fmt, env)
    super(StockPoll, self).__init__(url, message_format or default_format)

    def mung_data(self, data):
        """ Drill down to the result to make message_format more readable"""
        return super(StockPoll, self).mung_data(data['query']['results']['quote'])



def main():
    source = StockPoll("MSFT")
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink)


if __name__ == "__main__":
    main()
