/*
  Pi-Lite
 Copyright (c) 2013 Ciseco Ltd.
 Code written by Ciseco Ltd. April 4th 2013
 	2013-04-04 - V0.2 Initial beta release for internal testing
 	2013-05-02 - V0.3 Added new commands - scroll and display character
				  Added brief flash of a cross at startup

 Please see Readme.txt for details on the code functionality
 
 ///////////////////////////////////////////////////////////////////////
 ///////////////////////////////////////////////////////////////////////
 
 This code uses a modified version of the LOL Library LoLShield_V1
 This is based upon the LolShield Library here
 	http://code.google.com/p/lolshield/downloads/detail?name=LoLShield%20v23.zip
 	Library credits:
 	Created by Alex Wenger, December 30, 2009.
 	Modified by Matt Mets, May 28, 2010.
 	Modified by Ciseco Ltd. April 4th 2013
 
 */

#include "Charliplexing.h"
#include "Font.h"

#define ENTERTIMEOUT 5000
#define COMMANDTIMEOUT 15000

enum STATUS
{
  STATUS_INIT,
  STATUS_NORMAL,
  STATUS_SCROLL,
  STATUS_ONE,
  STATUS_TWO,
  STATUS_REPLACEONE,
  STATUS_WAITFORCOMMAND,
  STATUS_COMMAND,
};

byte scrolling=1;
byte status = STATUS_INIT;
byte commandchar=0;
char commandbuffer[128];
uint8_t commandbufferptr;
uint8_t commandcountx;
uint8_t commandcounty;
char currentchar=0;
byte currentpos;
uint32_t lastCharReceived;
int scrollDelay = 80;
uint32_t timer1;
uint8_t init_stage=0;
uint8_t init_pos;

/* -----------------------------------------------------------------  */
/** MAIN program Setup
 */
void setup()                    // run once, when the sketch starts
{
  Serial.begin(9600);
  Serial.println("Pi-Lite V0.3"); //Serial.flush();
  LedSign::Init();
  LedSign::Horizontal(4,127);
  LedSign::Vertical(6,127);
  delay(50);
  LedSign::Clear();
}


/* -----------------------------------------------------------------  */
/** MAIN program Loop
 */
void loop()                     // run over and over again
{
  switch (status)
  {
  case STATUS_INIT:
    if (Serial.available())
    {
      LedSign::Clear();
      status = STATUS_NORMAL;
    }
    else
    {
      switch (init_stage)
      {
      case 0:					// wait one second
        if (millis()-timer1 > 1000)	// delay one second
        {
          timer1 = millis();
          init_stage=1;
          LedSign::Horizontal(0,127);
          init_pos = 0;
        }
        break;
      case 1:					// scroll row down
        if (millis()-timer1 > 250)	// delay one quarter second
        {
          timer1 = millis();
          if (init_pos == 8)
          {
            init_stage=2;
          }
          else
          {
            LedSign::Horizontal(init_pos++,0);
            LedSign::Horizontal(init_pos,127);
          }
        }
        break;
      case 2:					// scroll row up
        if (millis()-timer1 > 250)	// delay one quarter second
        {
          timer1 = millis();
          if (init_pos == 0)
          {
            init_stage=3;
            LedSign::Clear();
            LedSign::Vertical(0,127);
          }
          else
          {
            LedSign::Horizontal(init_pos--,0);
            LedSign::Horizontal(init_pos,127);
          }
        }
        break;
      case 3:						// scroll column right
        if (millis()-timer1 > 250)	// delay one quarter second
        {
          timer1 = millis();
          if (init_pos == 13)
          {
            init_stage=4;
          }
          else
          {
            LedSign::Vertical(init_pos++,0);
            LedSign::Vertical(init_pos,127);
          }
        }
        break;
      case 4:						// scroll column left
        if (millis()-timer1 > 250)	// delay one quarter second
        {
          timer1 = millis();
          if (init_pos == 0)
          {
            init_stage=5;
            LedSign::Clear();
            Font::putChar(3,1,'P');
            Font::putChar(10,1,'i');
          }
          else
          {
            LedSign::Vertical(init_pos--,0);
            LedSign::Vertical(init_pos,127);
          }
        }
        break;
      case 5:			// wait for a char
        break;

      }
    }
    break;
  case STATUS_NORMAL:
  case STATUS_SCROLL:
    if (Serial.available())
    {
      byte c = Serial.peek();
      if (c != '$')
      {
        if (currentchar == 0)
        {
          c = readSerial();
          if (c)
          {
            currentchar = c;
            currentpos = 13;
            status = STATUS_SCROLL;
          }
        }
      }
      else
      {
        status = STATUS_ONE;
        readSerial();	// throw the $ away
      }
    }

    if (status == STATUS_SCROLL)
      scroll();
    else if (currentchar)  // if we are not scrolling and currchar is set then it needs clearing
      currentchar = 0;
    break;
  case STATUS_ONE:
  case STATUS_TWO:
    if (Serial.available())
    {
      if (Serial.peek() == '$')
      {
        if (status == STATUS_ONE)
        {
          status = STATUS_TWO;
        }
        else
        {
          status = STATUS_WAITFORCOMMAND;
          Serial.println("OK");
        }
        readSerial();	// throw the $ away
      }
      else if (currentchar == 0)
      {
        if (status == STATUS_ONE)
        {
          status = STATUS_SCROLL;
        }
        else
        {
          status = STATUS_REPLACEONE;
        }
        currentchar = '$';	// replace the '$'
        currentpos = 13;
      }
      else
      {
        status = STATUS_SCROLL;
      }
    }
    else if (millis() - lastCharReceived > ENTERTIMEOUT)
    {
      if (currentchar == 0)
      {
        if (status == STATUS_ONE)
        {
          status = STATUS_SCROLL;
        }
        else
        {
          status = STATUS_REPLACEONE;
        }
        currentchar = '$';	// replace the '$'
        currentpos = 13;
      }
      else
      {
        status = STATUS_SCROLL;
      }
    }
    break;
  case STATUS_REPLACEONE:
    if (currentchar == 0)
    {
      status = STATUS_SCROLL;
      currentchar = '$';	// replace the '$'
      currentpos = 13;
    }
    else
    {
      scroll();
    }
    break;
  case STATUS_WAITFORCOMMAND:	// waiting for a command
    commandchar = 0;
    commandbufferptr = 0;
  case STATUS_COMMAND:	// processing a command
    if (Serial.available())
    {
      processCommandChar(readSerial());
    }
    else if (millis() - lastCharReceived > COMMANDTIMEOUT)
    {
      status = STATUS_NORMAL;
    }
    break;

  }
}

///////////////////////////////////////////////////////////
// scrolling code
///////////////////////////////////////////////////////////
void scroll()
{
  static uint32_t scrolltime = millis();
  if (millis() - scrolltime > scrollDelay)
  {
    scrolltime = millis();
    LedSign::Scroll(1);
    // and draw the character if we have one
    if (currentchar)
    {
      byte colsleft = Font::putChar(currentpos--,1,currentchar);
      if (colsleft == 0)
      {
        currentchar = 0;
      }
    }
  }
}

void processCommandChar(char c)
{
  int iTmp;
  uint8_t row;
  char* ptr;
  uint8_t column;
  if (c == 0) return;	// just ignore

  if (commandchar == 0)
  {
    commandchar = c;
    commandbufferptr = 0;
    status = STATUS_COMMAND;
  }
  else
  {
    commandbuffer[commandbufferptr++] = c;
    if (commandbufferptr > 127)
    {
      // abandon command
      status = STATUS_NORMAL;
    }
    if (c == '\r')	// end of command
    {
      commandbuffer[--commandbufferptr] = 0;
      //Serial.print("CMD:"); Serial.println(commandbuffer);
      switch (commandchar)
      {
      case 'S':	// SPEEDnnn (1-1000) Set scrolling delay in mS 1 is scroll very fast, 1000 is scroll very slow.
		        // SCROLLnn - scroll left or right n columns
        if (0 == strncmp(commandbuffer,"PEED",4))
        {
          // this is a SPEED command
          scrollDelay = atoi(&commandbuffer[4]);
          if (scrollDelay == 0 ) scrollDelay = 1;
        }
        if (0 == strncmp(commandbuffer,"CROLL",5))
        {
          // this is a SCROLL command
          iTmp = atoi(&commandbuffer[4]);
          if (iTmp == 0 ) LedSign::Scroll(iTmp);
        }
        break;
      case 'T':	// Tc,r,char - display char at c,r
        column = atoi(commandbuffer);
        ptr = strchr(commandbuffer,',');
        if (ptr)
        {
          row = atoi(ptr+1);
          if (row > 0 && row < 15 && column > 0 && column < 10)
          {
            column--;
            row--;
			Font::putChar(column,row,commandbuffer[commandbufferptr-1]);
          }
        }
        break;
      case 'F':	// F01010110101 - set the frame bufer (one digit per pixel - 126 digits in total)
        if (commandbufferptr == 126)	// do we have the correct number of bytes?
        {
          commandbufferptr = 0;
          for (uint8_t x=0; x<14; x++)
          {
            for (uint8_t y=0; y<9; y++)
            {
              if (commandbuffer[commandbufferptr++] == '0')
                LedSign::Set(x,y,0);
              else
                LedSign::Set(x,y,1);
            }
          }
        }
        break;
      case 'B':	// Bc,val - Bargraph - (vertical 14 columns) set column c to val
        column = atoi(commandbuffer);
        ptr = strchr(commandbuffer,',');
        if (ptr)
        {
          row = atoi(ptr+1);	// this is the value 0-100%
          if (row >= 0 && row <= 100 && column > 0 && column < 15)
          {
            column--;	// adjust to zero based
            for (uint8_t y=0; y<9; y++)
            {
              if (((8-y)*100/9) < row)
                LedSign::Set(column,y,127);
              else
                LedSign::Set(column,y,0);
            }
          }
        }
        break;
      case 'V':	// Vr,val - Bargraph (horizontal 2 rows) set row n to val
        row = atoi(commandbuffer);
        ptr = strchr(commandbuffer,',');
        if (ptr)
        {
          column = atoi(ptr+1);	// this is the value 0-100%
          if (row > 0 && row < 3 && column >= 0 && column <= 100)
          {
            for (uint8_t y=0; y<4; y++)
            {
              uint8_t rowtoset = y;
              if (row==2) rowtoset+=5;
              for (uint8_t x=0; x<14; x++)
              {
                if ((x*100/14) < column)
                {
                  LedSign::Set(x,rowtoset,127);
                }
                else
                {
                  LedSign::Set(x,rowtoset,0);
                }
              }
            }
          }
        }
        break;
      case 'P':	// Pc,r,action - Set the pixel at column c, row r to action (ON,OFF,TOGGLE)
        column = atoi(commandbuffer);
        ptr = strchr(commandbuffer,',');
        if (ptr)
        {
          row = atoi(ptr+1);
          if (row > 0 && row < 15 && column > 0 && column < 10)
          {
            column--;
            row--;
            if (0 == strncmp(&commandbuffer[commandbufferptr-2],"ON",2))
              LedSign::Set(column,row,127);
            else if (0 == strncmp(&commandbuffer[commandbufferptr-3],"OFF",3))
              LedSign::Set(column,row,0);
            else if (0 == strncmp(&commandbuffer[commandbufferptr-6],"TOGGLE",6))
              LedSign::Tog(column,row);
          }
        }
        break;
      case 'A':	// ALL,ON - set all pixels on
        if (0 == strncmp(commandbuffer,"LL,ON",5))
        {
          LedSign::Clear(127);
        }
        else if (0 == strncmp(commandbuffer,"LL,OFF",6))
        {
          LedSign::Clear();
        }
        break;
      case 'G':	// Test code - switch Digital 14 on
        pinMode(14,OUTPUT);
        digitalWrite(14,HIGH);
        break;
      default:	// not a valid command
        break;
      }
      status = STATUS_NORMAL;
    }
  }
}


char readSerial()
{
  byte c = Serial.read();
  lastCharReceived = millis();
  if (c < 32 && c != '\r') return 0;	// throw away control characters
  return c;
}




