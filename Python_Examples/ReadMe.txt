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