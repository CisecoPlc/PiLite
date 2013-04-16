/*
  Grayscale Example

  Written by Jimmie Rodgers (jimmie@jimmieprodgers.com)
  
  History:
  	2012-01-14 - V0.0 Initial code

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330,
  Boston, MA 02111-1307, USA.
*/

#include "Charliplexing.h"  //initializes the LoL Sheild library

int xPosition = 0;          //x position 0-13
int yPosition = 0;          //y position 0-8
int frameCounter = 0;       //used to find when the frame has filled up (126 leds)
int greyscale = 0;          //greyscale color 0-7
int scrollSpeed = 100;      //delay between frames

void setup()                // run once, when the sketch starts
{
  LedSign::Init(GRAYSCALE); //initializes a grayscale frame buffer
}

void loop()                 // run over and over again
{ 
  //If the frame counter is full, then it delays for scrollSpeed.
  if(frameCounter == 126){
    delay(scrollSpeed);
    frameCounter=0;
  }
  
  //at the end of the row, it advances Y to the next one
  if(xPosition == 13)yPosition++;
  
  //at the end of the row, it starts from the first LED in the next one
  if(xPosition > 13)xPosition=0;
  
  //at the end of the frame, it starts from the begining again
  if(yPosition > 8)yPosition=0;
  
  //at the end of the colors, it starts from the begining
  if(greyscale > 7)greyscale=0;

  //sends the current x, y, and color to the frame, one LED at a time
  LedSign::Set(xPosition, yPosition, greyscale);

  //the counters are at the end of the loop, which will advance everything
  //for the next frame
  xPosition++;
  greyscale++;
  frameCounter++;
}