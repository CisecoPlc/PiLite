#!/usr/bin/env python
import urllib

import requests

from PiLiteTwitter import PiLiteBoard, poll_for_updates


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


class WeatherPoll(JSONPoll):
    def __init__(self, location, message_format=""):
        default_format = "{name}: {weather[0][description]}, {main[temp_c]:.0f}C"
	base_url = "http://api.openweathermap.org/data/2.5/weather?q=%s"
	super(WeatherPoll, self).__init__(base_url%location,
                                          message_format or default_format)

    def mung_data(self,data):
        """ Convert local temperature from K to C"""
        data['main']['temp_c'] = data['main']['temp']-273.15
        return super(WeatherPoll, self).mung_data(data)


class StockPoll(JSONPoll):
    def __init__(self, stock, message_format=""):
        """ Encoding a space in the url a + breaks YQL, so requests params
            handling can't be used
        """
        default_format = "{symbol} {DaysLow},{DaysHigh}"
	base_url = "http://query.yahooapis.com/v1/public/yql"
        querystring = "select * from yahoo.finance.quotes where symbol='%s'"
        fmt = "format=json"
        env = "env="+urllib.quote("store://datatables.org/alltableswithkeys")
        url = "%s?q=%s&%s&%s"%(base_url, urllib.quote(querystring%stock), fmt, env)
	super(StockPoll, self).__init__(url, message_format or default_format)

    def mung_data(self, data):
        """ Drill down to the result to make message_format more readable"""
        return super(StockPoll, self).mung_data(data['query']['results']['quote'])



def main():
    #source = WeatherPoll("London,uk")
    source = StockPoll("MSFT")
    sink = PiLiteBoard()
    print("ready")
    sink.write("ready  ")
    poll_for_updates(source, sink)


if __name__ == "__main__":
    main()
