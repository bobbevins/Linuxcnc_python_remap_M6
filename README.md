Linuxcnc Pure Python M6 Remap <H1>Biesse ROVER 346</H1>

This remap is 100% working and running in a production environment.
It has one ISO spindle 9KW, slots for 3 and the code allows for three spindles but not tested for three.
  Spindle 1 changes tool only. Tool 20 goes in spindle 2(B), tool 21 goes in spindle 3(C)
There are 33 drills and 10 horizontal drills mounted on 5 horizontal drill blocks
    tools 401-433 are individual drills
    tools 501,503.505,507,509 are paired horizontal drills
    tools >700 are drill groups or any combinaton of dirlls/horizontal drill pairs
          These drill groups are configured in the xml file in the remap directory.

An xml class created to easily change parameters within the remap, and for the remap to get common data.
ex. pulseDelay may be present in many sections of the remap, and all can be changed via one entry change 
in the xml. This class consists of the remap XML set within the remap, util.py and xmlBiesse.py
    
The python plugin was installed. I dont know if it is required but if you do install it, you need to have
the stdglue.py in the remap directory. Do not put the prolog or epilog in the remap statement in the ini.

ini remap statement: REMAP=M6 modalgroup=6 python=M6_Remap_BiesseRover346 

The 33 drill motor is energized in the remap and shutoff in the gcode(remapped M200) if a drill was used as last tool in the program. 
The drill motor gets shutoff within the remap near the beginning with the StopSpindleNow funtion.
I really need to configure it to follow spindle-on in the HAL when tool 400-700 are used, and remove the use in gcode.

I remap M400 to raise all spindles and make sure the drill motor is off. This is done because when the program ends the last spind/drill set that was used is left in the down position. M400 raises all spindles/drills. One of the first thing the remap does is raise all spindles including all drill sets.

This machine is in productions use and I will do very little changes, but will update this repo when I do.

Use at your own risk. I am not responsible, personally or finacially for any of this code, any hardware, any software or anything you do
if you choose to use it.

Many thanks to Michel Trahan, Sylvain Deschene, John Thorton, Andy Pugh and the whole linuxCNC community as their contribution
has been priceless.

Enjoy and let me know if you have success using it. contact me if you are having issues and I will try and help you.

Bob Bevins Group CNCT
bob.bevins AT cnctechproductions point com
