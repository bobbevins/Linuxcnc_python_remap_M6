Linuxcnc Pure Python M6 Remap

This remap is 100% working and running in a production environment.
It has one ISO spindle 9KW, slots for 3 and the code allows for three spindles but not tested for three.
  Spindle 1 changes tool only. Tool 20 goes in spindle 2 or (B), tool 21 goes in spindle 3 (C)
There are 33 drills and 10 horizontal drills mounted on 5 horizontal drill blocks
    tools 401-433 are individual drills
    tools 501,503.505,507,509 are paired horizontal drills
    tools >700 are drill groups or any combinaton of dirlls/horizontal drill pairs
          These drill groups are configured in the xml file in the remap directory.

An xml class created to easily change parameters within the remap. ex. pulseDelay may be 
present in many sections of the remap, and all can be changed via one entry change in the xml.
This class consists of the remap XML, util.py and 
    

We created an xml class used to get common values from xml file re: delay iterations.
We removed all yield's and INTTERP_EXECUTE_FINISH.

Make sure you import * from emccanon or else you wont get the commands and the sync's wont work.
