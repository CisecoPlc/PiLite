Pi-LITE example Python scripts

Can be run on the raspberry pi.

Install requirements:
PySerial, this can be installed with
$ sudo apt-get install python-serial




The first four can be ran from the the command line with out starting the GUI

BarScroll.py:
    Uses the bar-graph command $$$B?,? to scroll a wave across the screen

BarUpDown.py:
    Uses the bar-graph command $$$B?,? to scroll a wave up and down the screen

VUSameple.py:
    Uses the VU command $$$V?,? to demonstrate the VU's

Pacman.py:
    Uses the frame-buffer $$$F{0,1}*126 to show to simple frames of pac-man

The following two need to be run from a GUI so
$ startx 
then use LXTTerminal to run

These are interactive display using the built in python TK GUI interfaces

Bargraph_tk.py:
    14 Sliders that send out a bar-graph command for there given position

VU_tk.py:
    2 Sliders that send out a VU command for there given position
    


Pi-LITE Emulator

PiLiteEmulator.py:
    This is a stand alone virtual Pi-LITE created in python using Tkinter
    It Accpects all the same command as the real thing
    Just type into the Command Entry Box and try it out
    
Feed Examples 

The following reuqire a few more modules

Xively and reuests 
$ sudo apt-get install python-setuptools
$ sudo easy_install pip
$ sudo pip install xively-python

PiLiteLib.py:
    Core library file used by the following examples

PiLiteStock.py:
    Shows stock data from yahoo

PiLiteTwitter.py:
    Shows your home time line

PiLiteWeather.py:
    Shows weather from openweathermap.org

PiLiteWorldTime.py:
    Show world clock data

PiLiteXively.py:
    Show Xively Feed data