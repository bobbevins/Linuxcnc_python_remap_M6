#!/usr/bin/python
#from linuxcnc import INTERP_EXECUTE_FINISH, INTERP_OK
import remap

def __init__(self,**words):
    print len(words)," words passed"
    for w in words:
        print "%s: %s" % (w, words[w])

    
#def pi(self):
#	return 3.1415926535897932
