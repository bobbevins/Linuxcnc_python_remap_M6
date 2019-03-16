Linuxcnc Pure Python M6 Remap

Having trouble with interpreter ignoring commands when it gets to the epilog.
change_prolog and change_epilog are in the remap body. This was done because 
python is having issues with running three sequences in a row. the third one 
simply doesnt run. so we use REMAP=M6 modalgroup=6 python=M6_Remap_BiesseRover346
in the ini.

We created an xml class used to get common values from xml file re: delay iterations.
