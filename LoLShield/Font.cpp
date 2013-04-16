/*
  Font drawing library

  Copyright 2009/2010 Benjamin Sonntag <benjamin@sonntag.fr> http://benjamin.sonntag.fr/
  Modified by Ciseco Ltd. April 4th 2013
  
  History:
  	2010-01-01 - V0.0 Initial code at Berlin after 26C3
	2013-04-04 - V0.1 Re-written to support full font, CG Characters and proposrtional spacing
					  Font data also moved to PROGMEM.

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

#include "Font.h"
#include "Charliplexing.h"
#include <avr/pgmspace.h>
//#include "font_5x7.hpp"	// non-proportional font
#include "font_5x7_p.hpp"	// proportional font

// Custom character buffers - 8 characters available
// 8 cols * 6 rows - last byte of each char is the number of columns used
byte cgram [8][9] = { 
	{ 0xff, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xff, 0x08},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00} };


/*
 * Copy a character glyph from the myfont data structure to
 * display memory, with its upper left at the given coordinate
 * This is unoptimized and simply uses plot() to draw each dot.
 * returns number of columns that didn't fit
 */
// Display size and configuration, defaul is for a single 8x32 display
const byte xMax = 13; // 0 -> 13
const byte yMax = 8; // 0->8

uint8_t Font::putChar(int x, int y, char c) {
  // fonts defined for ascii 32 and beyond (index 0 in font array is ascii 32);
  // CGRAM characters are in range 0 to 15 with 8-15 being repeat of 0-7
  // note we force y to be modulo 8 - we do not support writing character to partial y values.

  byte charIndex;
  byte colData;
  byte numCols;
  byte chipno;
  byte addr;
  byte colsLeft = 0;		// cols that didn't fit

  if( c > 15 ) {
		// Regular characters
  		// replace undisplayable characters with blank;
  		if (c < 32 || c > 123) {
    			charIndex = 0;
  		} else {
    			charIndex = c - 32;
  		}

  		// move character definition, pixel by pixel, onto the display;
  		// fonts are defined as one byte per col;
		numCols=pgm_read_byte_near(&smallFont[charIndex][6]);	// get the number of columns this character uses
		for (byte col=0; col<numCols; col++) {
			colData = pgm_read_byte_near(&smallFont[charIndex][col]);
			if (x < 0) {
				x++;
				colsLeft++;
			} else if (x <= xMax && y <= yMax) {
				for (uint8_t i=0; i<8; i++)
				{
					LedSign::Set(x, y+i, colData & 1);
					colData >>= 1;
				}
				x++;
			} else {
				colsLeft++;
			}
		}
	
	} else {
	// CGRAM Characters
	charIndex = c & 0x07;		// Only low 3 bits count
	numCols=cgram[charIndex][8];	// get the number of columns this character uses
  	// fonts are defined as one byte per col;
    	for (byte col=0; col<numCols; col++) {
    		colData = cgram[charIndex][col];
			if (x < 0) {
				x++;
			} else if (x <= xMax) {
				for (uint8_t i=0; i<8; i++)
				{
					if (y <= yMax)
						LedSign::Set(x, y+i, colData & 1);
					colData >>= 1;
				}
				x++;
			} else {
				colsLeft++;
			}
		}
	}
  return colsLeft;
}

void Font::setCustomChar( int charNum, unsigned char cgchar[] ) {
	for(int i=0; i<8; i++ ) {
		cgram[charNum][i] = (byte)cgchar[i];
	}
	cgram[charNum][8] = 8;
}

void Font::setCustomChar( int charNum, unsigned char cgchar[], uint8_t numCols ) {
	for(int i=0; i<numCols; i++ ) {
		cgram[charNum][i] = (byte)cgchar[i];
	}
	cgram[charNum][8] = numCols;
}


