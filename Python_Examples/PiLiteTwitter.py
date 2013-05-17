#
#	LED Twitter Ticker - This Python script fetches the latest tweet from a given twitter
#						 account and sends its out via serial to the MSP430.  Once the MSP430
#						 has finished displaying the tweet it requests that the script sends the
#						 next tweet to be displayed.
#
#	Jan, 2012
#	By Matt Levine
#
#	Special thanks to:
#	pySerial
#	http://pyserial.sourceforge.net/
#	python-twitter
#	http://code.google.com/p/python-twitter/
#

import ConfigParser
import getopt
import os
import sys
from time import sleep
import twitter
import serial

'''
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

'''

class TweetRc(object):
  def __init__(self):
    self._config = None

  def GetConsumerKey(self):
    return self._GetOption('consumer_key')

  def GetConsumerSecret(self):
    return self._GetOption('consumer_secret')

  def GetAccessKey(self):
    return self._GetOption('access_key')

  def GetAccessSecret(self):
    return self._GetOption('access_secret')

  def _GetOption(self, option):
    try:
      return self._GetConfig().get('Tweet', option)
    except:
      return None

  def _GetConfig(self):
    if not self._config:
      self._config = ConfigParser.ConfigParser()
      self._config.read(os.path.expanduser('~/.tweetrc'))
    return self._config

index = 0;
twitterfeed = "@jcrouchley"

#api = twitter.Api()

rc = TweetRc()
consumer_key = rc.GetConsumerKey()
consumer_secret = rc.GetConsumerSecret()
access_key = rc.GetAccessKey()
access_secret = rc.GetAccessSecret()

api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_key,
                      access_token_secret=access_secret)

ser = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)

#user = api.GetUser(twitterfeed)
oldtext = ""


#print ser.portstr
ser.write("$$$SPEED50\r")
ser.write("ready  ")
sleep(2)

while True:
	try:
	        #user = api.GetUser(twitterfeed)
	        #status = user.GetStatus()
		statuses = api.GetHomeTimeline(since_id=None, max_id=None, count=1, page=None)
	        status = statuses[0]
	        text = "@" + status.GetUser().GetScreenName() + "::" + status.GetText()
	        text = text.encode('utf-8')
	        if text != oldtext:
		        oldtext = text
		        while len(text) > 0:
		                if len(text) > 14:
		                        ser.write(text[0:14])
		                        sleep(3)
		                        text = text[14:len(text)]
		                else:
		                        ser.write(text + "...")
		                        text = ""
	except URLError:
		ser.write("...oops... URL error ...")
        sleep(15)             

