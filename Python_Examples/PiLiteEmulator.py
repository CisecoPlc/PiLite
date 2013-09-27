#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Pi-LITE Emulator
    http://shop.ciseco.co.uk/pi-lite-lots-of-leds-for-the-raspberry-pi-0805-red/
    
    Copyright (c) 2013 Ciseco Ltd.
    Code written by Ciseco Ltd. June 15th 2013
 	2013-07-01 - V0.2 Initial release
    

"""
import Tkinter as tk
import time as time_
import sys, Queue, argparse, threading


class PiLITE(object):
    (STATUS_INIT, STATUS_NORMAL, STATUS_SCROLL, STATUS_ONE, STATUS_TWO,
     STATUS_REPLACEONE, STATUS_WAITFORCOMMAND, STATUS_COMMAND) = (0, 1, 2, 3,
                                                                  4, 5, 6, 7)
    ENTERTIMEOUT = 5000
    COMMANDTIMEOUT = 15000
                                                                  
    def __init__(self, master, **kwargs):
        self.master = master
        title=kwargs.pop('title')
        self.master.title(title)
        self.master.resizable(0,0)
    
        # variables
        self.xscale = 25
        self.yscale = 20
        self.xspacing = 4
        self.yspacing = 4
        self.leftPacking = 10
        self.rightPacking = 10
        self.topPacking = 50
        self.bottomPacking = 10
        self.rows = 9
        self.cols = 14
        self.font()
        
        self.buffer = bytearray()
        self.scrolling = 1
        self.status = self.STATUS_INIT
        self.commandchar = 0
        self.commandbuffer = bytearray()
        self.commandbufferptr = 0
        self.commandcountx = 0
        self.commandcounty = 0
        self.currentchar = 0
        self.currentpos = 0
        self.lastCharReceived = 0
        self.scrollDelay = 80
        self.timer1 = 0
        self.init_stage = 0
        self.init_pos = 0
        self.scrolltime = self.millis()
        self.onColour = 'red'
        self.offColour = 'grey'
        self.bgColour = 'dark green'

                
        self.logo = [0b111100000,0b101011111,0b111000001,
                     0b000000001,0b101100000,0b000011111,
                     0b000000000,0b000010000,0b000011111,
                     0b000010000,0b000000000,0b000011111,
                     0b010010101,0b100010101]
            
        
        #pixels[row][col]
        self.pixels = []            # canvas items
        self.shadowPixels = []      # current colour
        
        self.ke = (self.master.register(self.keyEntry), '%d', '%i', '%P', '%s',
                   '%S', '%v', '%V', '%W')
        self.initGui()
    
        self.master.after(1, self.loop)

    def initGui(self):
        frame = tk.Frame(self.master)
        frame.pack(expand=1, fill=tk.BOTH, padx=6, pady=6)
        
        tk.Button(frame, text='Quit', command=self.endApp).grid(row=0, column=1, stick=tk.E)
        
        self.canvas = tk.Canvas(frame,
                                width=self.leftPacking+(self.xscale*self.cols)+self.rightPacking,
                                height=self.topPacking+(self.yscale*self.rows)+self.bottomPacking,
                                bg=self.bgColour,
                                borderwidth=0, highlightthickness=0)
        self.canvas.grid(row=1, column=0, columnspan=2)
    
        self.canvas.create_text(
                                (self.leftPacking+(self.xscale*self.cols)+self.rightPacking)/2,
                                self.topPacking/2, text="Pi-LITE Emulator",
                                font=("Helvetica", "32"),
                                fill='white')
        for c in range(self.rows):
            self.pixels.append([])
            self.shadowPixels.append([])
            for r in range(self.cols):
                self.shadowPixels[c].append(self.offColour)
                self.pixels[c].append(
                      self.canvas.create_rectangle(self.leftPacking+(r*self.xscale)+self.xspacing,
                      self.topPacking+(c*self.yscale)+self.yspacing,
                      self.leftPacking+(r*self.xscale)+(self.xscale-self.xspacing),
                      self.topPacking+(c*self.yscale)+(self.yscale-self.yspacing),
                                                   fill=self.shadowPixels[c][r]))
    

        tk.Label(frame, text='Command Entry').grid(row=2, column=0)
        self.textInput = tk.Entry(frame, relief=tk.RAISED, validate='key',
                                  validatecommand=self.ke, )
        self.textInput.bind('<Return>', self.enterPress)
        self.textInput.grid(row=3, column=0, sticky=tk.W+tk.E, pady=2)
                
        
    def enterPress(self, *args):
        self.buffer.append('\r')
                
    def keyEntry(self, d, i, P, s, S, v, V, W):
        """
        print "d='%s'" % d
        print "i='%s'" % i
        print "P='%s'" % P
        print "s='%s'" % s
        print "S='%s'" % S
        print "v='%s'" % v
        print "V='%s'" % V
        print "W='%s'" % W
        """
        if d == '-1':
            return True
        if d == '0':
            return True
        elif S == '£':
            return False
        else:
            for c in range(len(S)):
                self.buffer.append(S[c])
            return True
    
    def loop(self):
        if self.status == self.STATUS_INIT:
            if (self.serAvailable()):
                dollarcount = 0
                if (self.serPeek() == '$'):		# we shortcut the init if $$$ is received
                    self.serRead()			# throw it away
                    dollarcount += 1
                    if (dollarcount >=3):
                        self.ledClear()
                        self.status = self.STATUS_WAITFORCOMMAND
                        self.serPrintln("OK")
                
                else:
                    if (self.init_stage == 5):
                        self.ledClear()
                        self.status = self.STATUS_NORMAL
                    else:
                        dollarcount = 0		# not a $ so ignore
                        self.serRead()			# throw it away
            
            else:
                if self.init_stage ==  0:					# wait one second
                    if (self.millis()-self.timer1 > 500):	# delay one second
                        self.timer1 = self.millis()
                        self.init_stage=1
                        self.ledHorizontal(0,127)
                        self.init_pos = 0
                
                elif self.init_stage ==  1:					# scroll row down
                    if (self.millis()-self.timer1 > 100):	# delay one quarter second
                        self.timer1 = self.millis()
                        if (self.init_pos == 8):
                            self.init_stage=2
                        else:
                            self.ledHorizontal(self.init_pos,0)
                            self.init_pos += 1
                            self.ledHorizontal(self.init_pos,127)
                
                elif self.init_stage ==  2:					# scroll row up
                    if (self.millis()-self.timer1 > 100):	# delay one quarter second
                        self.timer1 = self.millis()
                        if (self.init_pos == 0):
                            self.init_stage=3
                            self.ledClear()
                            self.ledVertical(0,127)
                        else:
                            self.ledHorizontal(self.init_pos,0)
                            self.init_pos -= 1
                            self.ledHorizontal(self.init_pos,127)
                    
                elif self.init_stage == 3:						# scroll column right
                    if (self.millis()-self.timer1 > 100):	# delay one quarter second
                        self.timer1 = self.millis()
                        if (self.init_pos == 13):
                            self.init_stage=4
                        else:
                            self.ledVertical(self.init_pos,0)
                            self.init_pos +=1
                            self.ledVertical(self.init_pos,127)

                elif self.init_stage ==  4:						# scroll column left
                    if (self.millis()-self.timer1 > 100):	# delay one quarter second
                        self.timer1 = self.millis()
                        if (self.init_pos == 0):
                            self.init_stage=5
                            self.ledClear()
                            #self.fontPutChar(3,1,'P')
                            #self.fontPutChar(10,1,'i')
                            self.displayLogo()
                        else:
                            self.ledVertical(self.init_pos,0)
                            self.init_pos -= 1
                            self.ledVertical(self.init_pos,127)
                      
                elif self.init_stage ==  5:			# wait for a char
                    pass
            
        elif self.status == self.STATUS_NORMAL or self.status == self.STATUS_SCROLL:
            if (self.serAvailable()):
                c = self.serPeek()
                if (c != '$'):
                    if (self.currentchar == 0):
                        c = self.readSerial()
                        if (c):
                            self.currentchar = c
                            self.currentpos = 13
                            self.status = self.STATUS_SCROLL
                
                else:
                    self.status = self.STATUS_ONE
                    self.readSerial()	# throw the $ away
            
            if (self.status == self.STATUS_SCROLL):
                self.scroll()
            
            elif (self.currentchar):  # if we are not scrolling and currchar is set then it needs clearing
                self.currentchar = 0
            
        elif self.status == self.STATUS_ONE or self.status == self.STATUS_TWO:
            if (self.serAvailable()):
                if (self.serPeek() == '$'):
                    if (self.status == self.STATUS_ONE):
                        self.status = self.STATUS_TWO
                    else:
                        self.status = self.STATUS_WAITFORCOMMAND
                        self.serPrintln("OK")
                    
                    self.readSerial()	# throw the $ away
                
                elif (self.currentchar == 0):
                    if (self.status == self.STATUS_ONE):
                        self.status = self.STATUS_SCROLL
                    else:
                        self.status = self.STATUS_REPLACEONE
                    
                    self.currentchar = '$'	# replace the '$'
                    self.currentpos = 13
                else:
                    self.status = self.STATUS_SCROLL
            
            elif (self.millis() - self.lastCharReceived > self.ENTERTIMEOUT):
                if (self.currentchar == 0):
                    if (self.status == self.STATUS_ONE):
                        self.status = self.STATUS_SCROLL
                    else:
                        self.status = self.STATUS_REPLACEONE
                    
                    self.currentchar = '$'	# replace the '$'
                    self.currentpos = 13
                else:
                    self.status = self.STATUS_SCROLL

        elif self.status == self.STATUS_REPLACEONE:
            if (self.currentchar == 0):
                self.status = self.STATUS_SCROLL
                self.currentchar = '$'	# replace the '$'
                self.currentpos = 13
            else:
                self.scroll()

        
        elif self.status == self.STATUS_WAITFORCOMMAND:	# waiting for a command
            self.commandchar = 0
            self.commandbuffer = bytearray()
            self.commandbufferptr = 0
            if (self.serAvailable()):
                self.processCommandChar(self.readSerial())
            elif (self.millis() - self.lastCharReceived > self.COMMANDTIMEOUT):
                self.status = self.STATUS_NORMAL

        elif self.status == self.STATUS_COMMAND:	# processing a command
            if (self.serAvailable()):
                self.processCommandChar(self.readSerial())
            elif (self.millis() - self.lastCharReceived > self.COMMANDTIMEOUT):
                self.status = self.STATUS_NORMAL
        
        self.master.after(100, self.loop)

    def processCommandChar(self, c):
        iTmp = 0
        row = 0
        ptr = 0
        column = 0
        if (c == 0):
            return	# just ignore
        
        if (self.commandchar == 0):
            self.commandchar = c
            self.commandbufferptr = 0
            self.status = self.STATUS_COMMAND
        else:
            self.commandbuffer.append(c)
            self.commandbufferptr += 1
            if (self.commandbufferptr > 127):
                # abandon command
                self.status = self.STATUS_NORMAL
            if (c == '\r'):	# end of command
                self.commandbufferptr -= 1
                self.commandbuffer.pop(self.commandbufferptr)
                #self.serPrint("CMD:") self.serPrintln(commandbuffer)
                if self.commandchar == 'S':	# SPEEDnnn (1-1000) Set scrolling delay in mS 1 is scroll very fast, 1000 is scroll very slow.
                    # SCROLLnn - scroll left or right n columns
                    if self.commandbuffer.startswith("PEED"):
                        # this is a SPEED command
                        self.scrollDelay = int(self.commandbuffer[4:])
                        if (self.scrollDelay == 0 ):
                            self.scrollDelay = 1
                    
                    if self.commandbuffer.startswith("CROLL"):
                        # this is a SCROLL command
                        iTmp = int(self.commandbuffer[5:])
                        if (iTmp != 0 ):
                            self.ledScroll(iTmp)
                    
                elif self.commandchar == 'T':	# Tc,r,char - display char at c,r
                    if (self.commandbuffer.find(',') != -1):
                        [column, row, char] = self.commandbuffer.split(',')
                        column = int(column)
                        row = int(row)
                        if (row > 0 and row < 15 and column > 0 and column < 10):
                            column -= 1
                            row -= 1
                            self.fontPutChar(column,row,char)
                    
                elif self.commandchar == 'F':	# F01010110101 - set the frame buffer (one digit per pixel - 126 digits in total)
                    if (self.commandbufferptr == 126):	# do we have the correct number of bytes?
                        self.commandbufferptr = 0
                        for x in range(14):
                            for y in range(9):
                                if (self.commandbuffer[self.commandbufferptr] == '0'):
                                    self.ledSet(x,y,0)
                                else:
                                    self.ledSet(x,y,1)
                                self.commandbufferptr += 1

                elif self.commandchar == 'B':	# Bc,val - Bargraph - (vertical 14 columns) set column c to val
                    if (self.commandbuffer.find(',') != -1):
                        [column, row] = self.commandbuffer.split(',')
                        column = int(column)
                        row = int(row)	# this is the value 0-100%
                        if (row >= 0 and row <= 100 and column > 0 and column < 15):
                            column -= 1	# adjust to zero based
                            for y in range(9):
                                if (((8-y)*100/9) < row):
                                    self.ledSet(column,y,127)
                                else:
                                    self.ledSet(column,y,0)

                elif self.commandchar == 'V':	# Vr,val - Bargraph (horizontal 2 rows) set row n to val
                    if (self.commandbuffer.find(',') != -1):
                        [row, column] = self.commandbuffer.split(',')
                        column = int(column) # this is the value 0-100%
                        row = int(row)
                        if (row > 0 and row < 3 and column >= 0 and column <= 100):
                            for y in range(4):
                                rowtoset = y
                                if (row==2):
                                    rowtoset+=5

                                for x in range(14):
                                    if ((x*100/14) < column):
                                        self.ledSet(x,rowtoset,127)
                                    else:
                                        self.ledSet(x,rowtoset,0)
                
                elif self.commandchar == 'P':	# Pc,r,action - Set the pixel at column c, row r to action (ON,OFF,TOGGLE)
                    if (self.commandbuffer.find(',') != -1):
                        [column, row, set] = self.commandbuffer.split(',')
                        column = int(column)
                        row = int(row)
                        if (row > 0 and row < 10 and column > 0 and column < 15):
                            column -= 1
                            row -= 1
                            if set.startswith("ON"):
                                self.ledSet(column,row,127)
                            elif set.startswith("OFF"):
                                self.ledSet(column,row,0)
                            elif set.startswith("TOGGLE"):
                                self.ledTog(column,row)

                elif self.commandchar == 'A':	# ALL,ON - set all pixels on
                    if str(self.commandbuffer).startswith("LL,ON"):
                        self.ledClear(127)
                    elif str(self.commandbuffer).startswith("LL,OFF"):
                        self.ledClear()

                else:	# not a valid command
                    pass
                self.status = self.STATUS_NORMAL

    def scroll(self):
        if (self.millis() - self.scrolltime > self.scrollDelay):
            self.scrolltime = self.millis()
            self.ledScroll(1)
            # and draw the character if we have one
            if (self.currentchar):
                colsleft = self.fontPutChar(self.currentpos,1,self.currentchar)
                self.currentpos -= 1
                if (colsleft == 0):
                    self.currentchar = 0
    
    def readSerial(self):
        c = self.serRead()
        self.lastCharReceived = self.millis()
        if (c < 32 and c != '\r'):
            return 0	# throw away control characters
        return c
    
    def displayLogo(self):
        for x in range(14):
                col = self.logo[x]
                for y in range(9):
                    self.ledSet(x, 8-y, 127 if (col & 0x01) else 0)
                    col >>= 1

    def millis(self):
        return int(round(time_.time() * 1000))

    def serRead(self):
        return chr(self.buffer.pop(0))


    def serPeek(self):
        return chr(self.buffer[0])

    def serAvailable(self):
        return len(self.buffer)

    def serPrintln(self, c):
        print(c)

    def serPrint(self, c):
        print(c),
    
    def ledSet(self, x, y, c=1):
        self.shadowPixels[y][x] = (self.onColour if c else self.offColour)
        self.canvas.itemconfig(self.pixels[y][x], fill=self.shadowPixels[y][x])

    def ledClear(self, set=0):
        for x in range(14):
            for y in range(9):
                self.shadowPixels[y][x] = (self.onColour if set else self.offColour)
                self.canvas.itemconfig(self.pixels[y][x], fill=self.shadowPixels[y][x])

    def ledTog(self, x, y):
        self.shadowPixels[y][x] = (self.onColour if self.shadowPixels[y][x] == self.offColour else self.offColour)
        self.canvas.itemconfig(self.pixels[y][x], fill=self.shadowPixels[y][x])
    
    def ledHorizontal(self, y, set=0):
        for x in range(14):
            self.shadowPixels[y][x] = (self.onColour if set else self.offColour)
            self.canvas.itemconfig(self.pixels[y][x], fill=self.shadowPixels[y][x])

    def ledVertical(self, x, set=0):
        for y in range(9):
            self.shadowPixels[y][x] = (self.onColour if set else self.offColour)
            self.canvas.itemconfig(self.pixels[y][x], fill=self.shadowPixels[y][x])

    def ledScroll(self, v):
        if (v < 0):
            # scroll right
            while (v):
                for x in reversed(range(14)):
                    for y in range(9):
                        self.shadowPixels[y][x] = self.shadowPixels[y][x-1]
                v += 1
        
            self.ledVertical(0,0)
        elif (v > 0):
            # scroll lef
            while (v):
                for x in range(1,14):
                    for y in range(9):
                        self.shadowPixels[y][x-1] = self.shadowPixels[y][x];
                v -= 1
        
        self.ledVertical(13,0)
        
        for x in range(14):
            for y in range(9):
                self.ledSet(x,y,(1 if self.shadowPixels[y][x] == self.onColour else 0))


    def fontPutChar(self, x, y, c):
        xMax = 13
        yMax = 8
        charIndex = 0
        colData = 0
        numCols = 0
        colsLeft = 0;		# cols that didn't fit
        
        if( c > 15 ):
            # Regular characters
            # replace undisplayable characters with blank;
            if (ord(c) < 32 or ord(c) > 123):
    			charIndex = 0;
            else:
    			charIndex = ord(c) - 32;
            # move character definition, pixel by pixel, onto the display;
            # fonts are defined as one byte per col;
            numCols = self.smallFont[charIndex][6]	# get the number of columns this character uses
            for col in range(numCols):
                colData = self.smallFont[charIndex][col]
                if (x < 0):
                    x += 1
                    colsLeft += 1
                elif (x <= xMax and y <= yMax):
                    for i in range(8):
                        self.ledSet(x, y+i, colData & 1)
                        colData >>= 1
                    x += 1
                else:
                    colsLeft += 1

        else:
        # CGRAM Characters
            charIndex = c & 0x07		# Only low 3 bits count
            numCols=cgram[charIndex][8]	# get the number of columns this character uses
            # fonts are defined as one byte per col;
            for col in range(numCols):
                colData = cgram[charIndex][col]
                if (x < 0):
                    x += 1
                elif (x <= xMax):
                    for i in range(8):
                        if (y <= yMax):
                            self.ledSet(x, y+i, colData & 1)
                        colData >>= 1
                    
                    x += 1
                else:
                    colsLeft += 1
        
        return colsLeft;

    def endApp(self):
        self.master.destroy()
        pass

    def font(self):
        #***** Small font (5x7) **********
        self.smallFont = [
                [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 4] ,   # sp
                [0x5f, 0x00, 0x00, 0x00, 0x00, 0x00, 2] ,   # !
                [0x07, 0x00, 0x07, 0x00, 0x00, 0x00, 4] ,   # "
                [0x14, 0x3e, 0x14, 0x3e, 0x14, 0x00, 6] ,   # #
                #[0x24, 0x2a, 0x7f, 0x2a, 0x12, 0x00, 6] ,   # $
                [0x48, 0x7e, 0x49, 0x4a, 0x20, 0x00, 6] ,   # $ == £
                [0x23, 0x13, 0x08, 0x64, 0x62, 0x00, 6] ,   # %
                [0x36, 0x49, 0x56, 0x20, 0x50, 0x00, 6] ,   # &
                [0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 2] ,   # '
                [0x1c, 0x22, 0x41, 0x00, 0x00, 0x00, 4] ,   # (
                [0x41, 0x22, 0x1c, 0x00, 0x00, 0x00, 4] ,   # )
                [0x2a, 0x1c, 0x7f, 0x1c, 0x2a, 0x00, 6] ,   # *
                [0x08, 0x08, 0x3E, 0x08, 0x08, 0x00, 6] ,   # +
                [0x50, 0x30, 0x00, 0x00, 0x00, 0x00, 3] ,   # ,
                [0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 6] ,   # -
                [0x60, 0x60, 0x00, 0x00, 0x00, 0x00, 3] ,   # .
                [0x20, 0x10, 0x08, 0x04, 0x02, 0x00, 6] ,   # /
                [0x3E, 0x51, 0x49, 0x45, 0x3E, 0x00, 6] ,   # 0
                [0x42, 0x7F, 0x40, 0x00, 0x00, 0x00, 4] ,   # 1
                [0x42, 0x61, 0x51, 0x49, 0x46, 0x00, 6] ,   # 2
                [0x22, 0x41, 0x49, 0x49, 0x36, 0x00, 6] ,   # 3
                [0x18, 0x14, 0x12, 0x7F, 0x10, 0x00, 6] ,   # 4
                [0x27, 0x45, 0x45, 0x45, 0x39, 0x00, 6] ,   # 5
                [0x3C, 0x4A, 0x49, 0x49, 0x30, 0x00, 6] ,   # 6
                [0x01, 0x71, 0x09, 0x05, 0x03, 0x00, 6] ,   # 7
                [0x36, 0x49, 0x49, 0x49, 0x36, 0x00, 6] ,   # 8
                [0x06, 0x49, 0x49, 0x49, 0x3E, 0x00, 6] ,   # 9
                [0x36, 0x36, 0x00, 0x00, 0x00, 0x00, 3] ,   # :
                [0x56, 0x36, 0x00, 0x00, 0x00, 0x00, 3] ,   # ;
                [0x08, 0x14, 0x22, 0x41, 0x00, 0x00, 5] ,   # <
                [0x14, 0x14, 0x14, 0x14, 0x14, 0x00, 6] ,   # =
                [0x41, 0x22, 0x14, 0x08, 0x00, 0x00, 5] ,   # >
                [0x02, 0x01, 0x51, 0x09, 0x06, 0x00, 6] ,   # ?
                [0x3e, 0x41, 0x5d, 0x55, 0x5E, 0x00, 6] ,   # @
                [0x7c, 0x12, 0x11, 0x12, 0x7c, 0x00, 6] ,   # A
                [0x7F, 0x49, 0x49, 0x49, 0x36, 0x00, 6] ,   # B
                [0x3E, 0x41, 0x41, 0x41, 0x22, 0x00, 6] ,   # C
                [0x7F, 0x41, 0x41, 0x41, 0x3e, 0x00, 6] ,   # D
                [0x7F, 0x49, 0x49, 0x49, 0x41, 0x00, 6] ,   # E
                [0x7F, 0x09, 0x09, 0x09, 0x01, 0x00, 6] ,   # F
                [0x3E, 0x41, 0x49, 0x49, 0x3A, 0x00, 6] ,   # G
                [0x7F, 0x08, 0x08, 0x08, 0x7F, 0x00, 6] ,   # H
                [0x41, 0x7F, 0x41, 0x00, 0x00, 0x00, 4] ,   # I
                [0x20, 0x40, 0x40, 0x3F, 0x00, 0x00, 5] ,   # J
                [0x7F, 0x08, 0x14, 0x22, 0x41, 0x00, 6] ,   # K
                [0x7F, 0x40, 0x40, 0x40, 0x40, 0x00, 6] ,   # L
                [0x7F, 0x02, 0x0C, 0x02, 0x7F, 0x00, 6] ,   # M
                [0x7F, 0x02, 0x04, 0x08, 0x7F, 0x00, 6] ,   # N
                [0x3E, 0x41, 0x41, 0x41, 0x3E, 0x00, 6] ,   # O
                [0x7F, 0x09, 0x09, 0x09, 0x06, 0x00, 6] ,   # P
                [0x3E, 0x41, 0x51, 0x21, 0x5E, 0x00, 6] ,   # Q
                [0x7F, 0x09, 0x19, 0x29, 0x46, 0x00, 6] ,   # R
                [0x26, 0x49, 0x49, 0x49, 0x32, 0x00, 6] ,   # S
                [0x01, 0x01, 0x7F, 0x01, 0x01, 0x00, 6] ,   # T
                [0x3F, 0x40, 0x40, 0x40, 0x3F, 0x00, 6] ,   # U
                [0x1F, 0x20, 0x40, 0x20, 0x1F, 0x00, 6] ,   # V
                [0x3F, 0x40, 0x38, 0x40, 0x3F, 0x00, 6] ,   # W
                [0x63, 0x14, 0x08, 0x14, 0x63, 0x00, 6] ,   # X
                [0x07, 0x08, 0x70, 0x08, 0x07, 0x00, 6] ,   # Y
                [0x61, 0x51, 0x49, 0x45, 0x43, 0x00, 6] ,   # Z
                [0x7F, 0x41, 0x41, 0x00, 0x00, 0x00, 4] ,   # [
                [0x55, 0x2A, 0x55, 0x2A, 0x55, 0x00, 6] ,   # 55	??
                [0x41, 0x41, 0x7F, 0x00, 0x00, 0x00, 4] ,   # ]
                [0x04, 0x02, 0x01, 0x02, 0x04, 0x00, 6] ,   # ^
                [0x40, 0x40, 0x40, 0x40, 0x40, 0x00, 6] ,   # _
                [0x01, 0x02, 0x04, 0x00, 0x00, 0x00, 4] ,   # '
                [0x20, 0x54, 0x54, 0x78, 0x00, 0x00, 5] ,   # a
                [0x7F, 0x44, 0x44, 0x38, 0x00, 0x00, 5] ,   # b
                [0x38, 0x44, 0x44, 0x44, 0x00, 0x00, 5] ,   # c
                [0x38, 0x44, 0x44, 0x7F, 0x00, 0x00, 5] ,   # d
                [0x38, 0x54, 0x54, 0x58, 0x00, 0x00, 5] ,   # e
                [0x04, 0x7E, 0x05, 0x01, 0x00, 0x00, 5] ,   # f
                [0x08, 0x54, 0x54, 0x3c, 0x00, 0x00, 5] ,   #
                [0x7F, 0x08, 0x04, 0x78, 0x00, 0x00, 5] ,   # h
                [0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 2] ,   # i
                [0x20, 0x40, 0x3D, 0x00, 0x00, 0x00, 4] ,   # j
                [0x7F, 0x10, 0x28, 0x44, 0x00, 0x00, 5] ,   # k
                [0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 2] ,   # l
                [0x78, 0x04, 0x18, 0x04, 0x78, 0x00, 6] ,   # m
                [0x7c, 0x08, 0x04, 0x78, 0x00, 0x00, 5] ,   # n
                [0x38, 0x44, 0x44, 0x38, 0x00, 0x00, 5] ,   # o
                [0x7C, 0x14, 0x14, 0x08, 0x00, 0x00, 5] ,   # p
                [0x08, 0x14, 0x14, 0x7C, 0x00, 0x00, 5] ,   # q
                [0x7C, 0x08, 0x04, 0x04, 0x00, 0x00, 5] ,   # r
                [0x48, 0x54, 0x54, 0x24, 0x00, 0x00, 5] ,   # s
                [0x04, 0x7F, 0x44, 0x00, 0x00, 0x00, 4] ,   # t
                [0x3C, 0x40, 0x40, 0x3c, 0x00, 0x00, 5] ,   # u
                [0x0C, 0x30, 0x40, 0x30, 0x0c, 0x00, 6] ,   # v
                [0x3C, 0x40, 0x30, 0x40, 0x3C, 0x00, 6] ,   # w
                [0x44, 0x28, 0x10, 0x28, 0x44, 0x00, 6] ,   # x
                [0x0C, 0x50, 0x50, 0x3c, 0x00, 0x00, 5] ,   # y
                [0x44, 0x64, 0x54, 0x4C, 0x44, 0x00, 6] ,   # z
                [0x06, 0x09, 0x09, 0x06, 0x00, 0x00, 5]     # ∫
                ]

if __name__=='__main__':
    root = tk.Tk()
    app = PiLITE(root,title='Pi-LITE v0.2')
    root.mainloop()
