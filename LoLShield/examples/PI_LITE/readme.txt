PI-LITE shipping software

Default baud rate is 9600
All commands are preceeded by $$$ and terminated with <CR>
If no data is received for x seconds then the command is terminated and ignored
<LF> and other control characters are ignored at all times.
As soon as $$$ is received then any scrolling stops, scrolling will start again when a non-command character is received
If invalid data received whilst expecting a command character then the command is terminated and ignored
Any data received otherwise switches the display to scroll mode and displays the character via scrolling

Pixel (1,1) is upper left and (14,9) is lower right.

Powerup
=======
On powerup the PI-Lite will send identification and version down the serial port "Pi-Lite version n.n"
The following can be interrupted at any time by a $$$ or a character to scroll.
1) delay for 1 second
2) scroll a single row down and up
3) scroll a single column right and left
4) Display Pi-Lite Logo

Commands
========
$$$SPEEDval Set scrolling delay in mS 1 is scrolling very fast, 1000 is scrolling very slow.
$$$F01010110101 - set the frame buffer (one digit per pixel - 126 digits in total) 
				  Format: Columns left to right starting at the top.
				  e.g. (1,1) ... (1,9)(2,1)...(2,9) etc.
$$$Bc,val - Bargraph - (vertical 14 columns) set column c (1-14) to val
$$$Vr,val - Bargraph (horizontal 2 rows) set row r (1-2) to val
$$$Pc,r,action - Set the pixel at column c (1-15), row r(1-9) to action (ON,OFF,TOGGLE)
$$$ALL,ON - set all pixels on
$$$ALL,OFF - set all pixels off
