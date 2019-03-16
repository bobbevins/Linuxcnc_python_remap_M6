#!/usr/bin/env python
# Mar 2017 Code by Michel Trahan, Bob Bevins and Sylvain Deschene
# Remap of M6 in Pure Python, remap.py includes change_epilog
# Machine is Biesse 346 1995, with 3 position rack toolchanger
#-----------------------------------------------------------------------------------
import linuxcnc
from interpreter import *
from emccanon import MESSAGE, SET_MOTION_OUTPUT_BIT, CLEAR_MOTION_OUTPUT_BIT,SET_AUX_OUTPUT_BIT,CLEAR_AUX_OUTPUT_BIT
from util import lineno
#-----------------------------------------------------------------------------------
throw_exceptions = 1 # raises InterpreterException if execute() or read() fail
#-----------------------------------------------------------------------------------
#from stdglue import change_prolog, change_epilog
import xmlBiesse
import sys



#------------------------------------------------------------------------------------------------------
# MAIN FUNCTION : change_remap 
#
# from REMAP=M6 modalgroup=6 prolog=change_prolog python=M6_Remap_BiesseRover346  epilog=change_epilog
#       - change_prolog is in stdglue.py, change_epilog is in remap.py.
#------------------------------------------------------------------------------------------------------
# when done, change the world coordinate system to reflect the new offsets for the selected spindle
#   (G10 L20 X0 Y0 Z0) ...
#
#-------------------------------------------------------------------------------------------------------------------
#   REMAP=M6 modalgroup=6 prolog=change_prolog   python=M6_Remap_BiesseRover346  epilog=change_epilog
#-------------------------------------------------------------------------------------------------------------------
def queuebuster(self, **words):
    yield INTERP_EXECUTE_FINISH
    
def M6_Remap_BiesseRover346(self, **words):
    #--------------------------------------------------
    # if in preview mode exit without doing anything and all ok
    #----------------------------------------------------------
    if self.task==0:
        return INTERP_OK
    #else:
    #    DoYield()

    change_prolog1(self, **words)
	
    try:
        #--------------------------------------------------------------------
        #   Get the xmlfile path from the ini file ... or hardcode here
        #--------------------------------------------------------------------
        # [XML]
        # FILE=/home/bob/linuxcnc/configs/python/BiesseRover346.xml
        #--------------------------------------------------------------------
		
		
        
		
        xmlfile = "/home/bob/linuxcnc/configs/python/BiesseRover346.xml"
        #---------------------------------------------------------------------
        #   XML - Objects to fetch needed infos ...
        #---------------------------------------------------------------------
        #queuebuster(self, **words)
        self.x = xmlBiesse.xmlBiesse(xmlfile) # the xml interface
        # set some self values 
        self.feedSpeed  = self.x.getFeedSpeed()
        self.pulseDelay = self.x.getDelay("pulseDelay")
        self.stat = linuxcnc.stat()
        self.HIGH = 1
		
        StopSpindleNow(self)
        #--------------------------------------
		#Set tool-prepared for iocontrol
        #set_tool_prepared(self, **words) 		
        # -------------------------------------
        # test if spindle has really stopped
        self.stat.poll()
        index = self.x.getSignalInfos("spindleHasStopped")
        isSpindleStopped = int(self.stat.din[index])
        if isSpindleStopped != 1:
            msg = "Spindle has not stopped even after M66"
            self.set_errormsg(msg)
            return ReturnERROR()
        
        #------------------------------------------------------------------
        # we are good to go
        #------------------------------------------------------------------
        print("Spindle Stopped")
        #-----------------------
        # raise the Z
        #-----------------------
        MoveZtoZero(self)
        #----------------------------------------------
        
        #-----------------------
        # raise all spindles
        #-----------------------
        print("Lets just try raising A,B and C for now")
        raisespindlesABC(self)
        #raiseALLspindles(self)
        print("ALL Spindle Raised")
        #--------------------------
        # De Energise all spindles
        #--------------------------
        DeEnergiseALLSpindle(self)
        print("ALL Spindles DeEnergised")
        #---------------------------------------------------------------------------------
        # now go according to selected_tool given by linuxcnc for the Txxx M6 ngc command
        #---------------------------------------------------------------------------------
        selectedtool = int(self.params["selected_tool"])
        self.selected_tool = int(self.params["selected_tool"])
        print("Selected Tool : %d" % selectedtool)
        if selectedtool > 700:                                  # 701 to ... any combinations of drills and side drills
            DropTools(self, selectedtool)
            self.current_tool = selectedtool
            self.current_pocket = selectedtool
        elif (selectedtool > 500 and selectedtool < 510):       # 5 pairs of side drills (1,3,5,7,9)
            DropSideDrill(self, selectedtool - 500)
            self.current_tool = selectedtool
            self.current_pocket = selectedtool
        elif (selectedtool > 400 and selectedtool < 434):       # 33 drills (1-33)
            DropDrill(self, selectedtool - 400)
            self.current_tool = selectedtool
            self.current_pocket = selectedtool
        else:
            if selectedtool == 21:
                if SpindleHasTool(self, "C"):
                    DropSpindleC(self)
                    EnergiseSpindle(self, "C")
                    #return ReturnOK()
                    return INTERP_OK
                else:
                    msg = "Spindle C has no tool"
                    self.set_errormsg(msg)
                    return ReturnERROR()
            elif selectedtool == 20:
                if SpindleHasTool(self, "B"):
                    DropSpindleB(self)
                    EnergiseSpindle(self, "B")
                    SetG43Tool20(self)
                    #return ReturnOK()
                    return INTERP_OK
                else:
                    msg = "Spindle B has no tool"
                    self.set_errormsg(msg)
                    return ReturnERROR()
            elif selectedtool > 0 and selectedtool < 4: #only 3 tools for A (1, 2, 3)
                EnergiseSpindle(self, "A")


                # now time to see if already in spindle
                freePocket = FindFreePocket(self)
                self.current_pocket = freePocket
                print("freePocket = %s" % freePocket)
                currenttool = int(self.params["tool_in_spindle"])
                print("tool in spindle = %s" % currenttool)
                if freePocket == -1:
                    # what is in spindle 1 ? check if spindle has tool
                    if SpindleHasTool(self, "A"): # we have a problem
                        msg = "No Free Pockets and Spindle A has a tool"
                        self.set_errormsg(msg)
                        return ReturnERROR()
                    else: # if not, go get the one needed
                        #------------------------------------------
                        # PICKUP selected tool in according pocket
                        #------------------------------------------
                        print("Spindle A has no tool, going to PickUpNewTool %d" % selectedtool)
                        OpenCasket(self)
                        if selectedtool == 1:       #Pickup Tool 1
                            PickUpTool1(self)                            
                            CloseCasket(self)
#                            self.current_tool = 1
                        elif selectedtool == 2:     #Pickup Tool 2
                            PickUpTool2(self)
                            #SetG43Tool2(self)
                            CloseCasket(self)
#                            self.current_tool = 2
                        elif selectedtool == 3:     #Pickup Tool 3
                            PickUpTool3(self)
                            CloseCasket(self)
#                            self.current_tool = 3
							
                        self.current_tool = selectedtool
                        self.current_pocket = selectedtool
						
                        return INTERP_OK    
                else:
                    print("There is a free pocket")
                    #-------------------------------------------------------
                    # check if spindle has tool
                    #-------------------------------------------------------
                    if not SpindleHasTool(self, "A"):
                        msg = "Error while droping a tool, Spindle A has no tool to drop"
                        self.set_errormsg(msg) # replace builtin error message
                        return ReturnERROR()
                    print("Spindle A has tool, do drop it")
                    #-------------------------------------------------------
                    # check if tool already in spindle
                    #-------------------------------------------------------
                    if freePocket == selectedtool:
                        DropSpindleA(self)
                        print("Spindle A already has the right tool")
                        self.current_tool = selectedtool
                        self.current_pocket = selectedtool
                        return INTERP_OK
                    #------------------------------------
                    # DROP current tool in free pocket
                    #------------------------------------
                    OpenCasket(self)
                    if freePocket == 1:
                         
                        DropTool1(self)
                        if selectedtool == 2:
                            PickUpTool2(self)
                        elif selectedtool ==3:
                            PickUpTool3(self)
                        CloseCasket(self)
                        DropSpindleA(self)
                        self.current_tool = selectedtool
                        self.current_pocket = selectedtool
                        return INTERP_OK
                        
                    elif freePocket == 2:
                        
                        DropTool2(self)
                        if selectedtool == 1:
                            PickUpTool1(self)
                        elif selectedtool ==3:
                            PickUpTool3(self)
                        CloseCasket(self)
                        DropSpindleA(self)
                        self.current_tool = selectedtool
                        self.current_pocket = selectedtool
                        return INTERP_OK
                        
                    elif freePocket == 3:

                        DropTool3(self)
                        if selectedtool == 2:
                            PickUpTool2(self)
                        elif selectedtool ==1:
                            PickUpTool1(self)
                        CloseCasket(self)
                        DropSpindleA(self)
                        self.current_tool = selectedtool
                        self.current_pocket = selectedtool
                        return INTERP_OK
                   
            
                        
            else: # not > 700, not between 400 and 434 (exclusive), not between 500 and 510 (exclusive), nor 0,1,2,3,10,11
                msg  = "Wrong tool number either 0 to remove it from spindle or 1,2,3,20,21\n"
                msg += "Or 401 to 433 for drills, 501, 503, 505, 507, 509 for side drills,\n"
                msg += "701 to whatever is defined in the tool table AND the xml file\n"
                msg += "Tool given was: %d" %  selectedtool
                self.set_errormsg(msg) # replace builtin error message
                return ReturnERROR()
                
    #-----------------------------------------
    # We have errors ! catch and return error
    #-----------------------------------------
#    except InterpreterException,e:
#        msg = "BOB look at this error : %d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
#        self.set_errormsg(msg) # replace builtin error message
        print("%s" % msg)
        return ReturnERROR()

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return ReturnERROR()
    except ValueError:
        print "Could not convert data to an integer."
        return ReturnERROR()
    except ZeroDivisionError as detail:
        print 'Handling run-time error:', detail
        return ReturnERROR()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
   
    finally:
        #change_epilog(self, **words)
 
    
        print 'Hold on, off to epilog coming up!'
        print("Current pocket = %s" % self.current_pocket)
        print("Selected pocket = %s" % self.selected_pocket)
        print("Param.Selected pocket = %s" % int(self.params["selected_pocket"]))
        print("Current tool in spindle = %s" % self.current_tool)
        print("Selected tool = %s" % self.selected_tool)
        
        self.return_value = self.selected_tool
    #-----------------------
    # all fine, return ok !
    #-----------------------
#       
        print 'Final!'
        print("Self return value = %s" % self.return_value)
		print 'calling epilog'
        epilog(self, **words)
		print 'Returned form epilog journey'
		print("Current pocket = %s" % self.current_pocket)
        print("Selected pocket = %s" % self.selected_pocket)
        print("Param.Selected pocket = %s" % int(self.params["selected_pocket"]))
        print("Current tool in spindle = %s" % self.current_tool)
        print("Selected tool = %s" % self.selected_tool)
		print 'exiting remap'
		
    return INTERP_OK
    #ReturnOK()

#----------------------------------------------------------
#----------------------------------------------------------
def change_prolog1(self, **words):
    try:
        if self.selected_pocket < 0:
            return "M6: no tool prepared"

        if self.cutter_comp_side:
            return "Cannot change tools with cutter radius compensation on"

        self.params["tool_in_spindle"] = self.current_tool
        self.params["selected_tool"] = self.selected_tool
        self.params["current_pocket"] = self.current_pocket
        self.params["selected_pocket"] = self.selected_pocket
        return INTERP_OK
    except Exception, e:
        return "M6/change_prolog: %s" % (e)

def change_epilog1(self, **words):
    try:
            #print("Change epilog executing....")
            if self.return_value > 0.0:
                print("pass return value")
                self.selected_pocket =  int(self.params["selected_pocket"])
                print("before emccannon CHANGE TOOL")
                emccanon.CHANGE_TOOL(self.selected_pocket)
                print("emccannon CHANGE TOOL sent")
                self.current_pocket = self.selected_pocket
                self.selected_pocket = -1
                self.selected_tool = -1
                # cause a sync()
                print("Lets Sync this Bitch, NOW")
                self.set_tool_parameters()
                self.toolchange_flag = True
                yield INTERP_EXECUTE_FINISH
            else:
                self.set_errormsg("M6 aborted (return code %.1f)" % (self.return_value))
                return
    except Exception, e:
        self.set_errormsg("M6/change_epilog: %s" % (e))
        return 

#def set_tool_prepared(self)
#    self.execute("M65 P55")		
		
#def change_epilog(self, **words):
#    try:
#        if self.return_value > 0.0:
#            print 'Finally!'
#            # commit change
#            self.selected_pocket =  int(self.params["selected_pocket"])
#            emccanon.CHANGE_TOOL(self.selected_pocket)
#            self.current_pocket = self.selected_pocket
#            #self.selected pocket = -1
#            #self.selected_tool = -1			
#            # cause a sync()
#            #self.tool_change_flag = True
#            self.set_tool_parameters()
#            self.toolchange_flag = true
#            yield INTERP_EXECUTE_FINISH
#        else:
#             self.set_errormsg("M6 aborted (return code %.1f)" % (self.return_value))
#             yield INTERP_ERROR
#     except Exception, e:
#             self.set_errormsg("M6/change_epilog: %s" % (e))
#     yield INTERP_ERROR





#----------------------------------------------------------
#-----Set me some tool offsets here!!!---------------------
#----------------------------------------------------------
def SetG43Tool20(self):
    self.execute("G43 H20")
    
def SetG43Tool2(self):
    self.execute("G43 H2")    
#----------------------------------------------------------
def DropSpindleA(self):
    self.execute("M64 P2")                      #Drop Spindle
    self.execute("G4 P1")                       #wait to release pulse on lock spindle
    self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
    self.execute("M66 P9 L3 Q5")  
    print("drop Spindle A Done")              #Wait for Spindle to drop
    
def DropSpindleB(self):
    index = self.x.getSignalInfos("spindleBdrop")
    self.execute("M64 P%d" % index)
    self.execute("G4 P0.5")
    self.execute("M65 P%d" % index)
    index = self.x.getSignalInfos("spindleBdown")
    self.execute("M66 P%d L4 Q1" % index)
    #self.execute("M64 P3")
    #self.execute("G4 P0.5")
    #self.execute("M65 P3")
    #self.execute("M66 P10 L4 Q1")
    print("DropSpindle(B) done")

def DropSpindleC(self):
    self.execute("M64 P4")
    self.execute("G4 P0.5")
    self.execute("M65 P4")
    self.execute("M66 P11 L4 Q1")
    print("DropSpindle(C) done")    
    



def DropTool1(self):

    #id = 1
    #posX, posY, posZ = self.x.getPocketPos(id, "Front")
    self.execute("G53 G0 X15.375 Y-25.57 Z0")   #Move to front of pocket 1
    #self.execute("G53 G0 F%d X%f Y%f Z0.0" % (self.feedSpeed, posX, posY), lineno())
    self.execute("M64 P2")                      #Drop Spindle A
    self.execute("M66 P9 L3 Q5")                #Wait for Spindle to drop
    self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
    self.execute("M64 P10")                     #raise Pocket 1
    self.execute("M66 P17 L3 Q5")               #wait for Pocket to raise
    self.execute("G53 G0 Z-1.788")              #Drop the Z into position
    #self.execute("G53 G0 F%d Z%f" % (self.feedSpeed, posZ), lineno())
    self.execute("G53 G1 F200 X11.825")         #Move into pocket to release tool
    #posX2, posY2, posZ2 = self.x.getPocketPos(id, "Top")
    #self.execute("G53 G1 F%d X%f " % (self.feedSpeed, posX2),lineno())
    self.execute("M66 P4 L3 Q5")                #Wait for pocket 1 has tool
    self.execute("M64 P8")                      #Release Spindle

    self.execute("M66 P13 L3 Q5")               #Wait for Spindle to release
    self.execute("M64 P5")                      #Raise Spindle
    self.execute("M66 P7 L3 Q5")                #Wait for Spindle to raise
    self.execute("G53 G0 Z0")                   #Move to Z0
    self.execute("M65 P8")                      #Release Sp A pulse relay, only needs pulse
    self.execute("M64 P9")                      #Lock Spindle A
    self.execute("G4 P1.0")                     #wait to release pulse on lock spindle
    self.execute("M65 P9")                      #release Lock Spindle A, only needs pulse    
    self.execute("M65 P10")                     #Lower Pocket 1
    self.execute("G53 G0 X15.375 Y-25.57 Z0")   #Move to front of pocket 1   
    #self.execute("G53 G0 F%d X%f Y%f Z0.0" % (self.feedSpeed, posX, posY), lineno())
    #self.execute("G1 G53 F%d Z%f" % (self.feedSpeed, posZ), lineno())
    #INTERP_EXECUTE_FINISH
#---------------------------------------------------------------------
def DropTool2(self):
    self.execute("G53 G0 X15.375 Y-33.527 Z0")  #Move to front of pocket 2
    self.execute("M64 P2")                      #Drop Spindle
    self.execute("M66 P9 L3 Q5")                #Wait for Spindle to drop
    self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
    self.execute("M64 P11")                     #raise Pocket 2
    self.execute("M66 P18 L3 Q5")              #wait for Pocket to raise
    self.execute("G53 G0 Z-1.840")              #Drop the Z into position
    self.execute("G53 G1 F200 X11.900")         #Move into pocket to release tool
    #self.execute("M66 P5 L3 Q5")                #Wait for pocket 2 has tool
    self.execute("M64 P8")                      #Release Spindle
    self.execute("M66 P13 L3 Q5")               #Wait for Spindle to release
    self.execute("M64 P5")                      #Raise Spindle
    self.execute("M66 P7 L3 Q5")                #Wait for Spindle to raise
    self.execute("G53 G0 Z0")                   #Move to Z0
    self.execute("M65 P8")                      #Release Sp B pulse relay, only needs pulse
    self.execute("M64 P9")                      #Lock Spindle A
    self.execute("G4 P1.0")                     #wait to release pulse on lock spindle
    self.execute("M65 P9")                      #release Lock Spindle A, only needs pulse
    self.execute("M65 P11")                     #Lower Pocket 2
    self.execute("G53 G0 X15.375 Y-33.527 Z0")   #Move to front of pocket 2
    #INTERP_EXECUTE_FINISH
#---------------------------------------------------------------------
def DropTool3(self):
    self.execute("G53 G0 X15.375 Y-41.545 Z0")  #Move to front of pocket 3
    self.execute("M64 P2")                      #Drop Spindle
    self.execute("M66 P9 L3 Q5")                #Wait for Spindle to drop
    self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
    self.execute("M64 P12")                     #raise Pocket 3
    self.execute("M66 P19 L3 Q5")               #wait for Pocket to raise

    self.execute("G53 G0 Z-1.790")              #Drop the Z into position
    self.execute("G53 G1 F200 X11.825")         #Move into pocket to release tool
    #self.execute("M66 P6 L3 Q5")                #Wait for pocket 3 has tool
    self.execute("M64 P8")                      #Release Spindle 
    self.execute("M66 P13 L3 Q5")               #Wait for Spindle to release
    self.execute("M64 P5")                      #Raise Spindle
    self.execute("M66 P7 L3 Q5")                #Wait for Spindle to raise
    self.execute("G53 G0 Z0")                   #Move to Z0
    self.execute("M65 P8")                      #Release Sp B pulse relay, only needs pulse
    self.execute("M64 P9")                      #Lock Spindle A
    self.execute("G4 P1.0")                     #wait to release pulse on lock spindle
    self.execute("M65 P9")                      #release Lock Spindle A, only needs pulse    
    self.execute("M65 P12")                     #Lower Pocket 3
    self.execute("G53 G0 X15.375 Y-41.545 Z0")  #Move to front of pocket 3  
    #INTERP_EXECUTE_FINISH
#---------------------------------------------------------------------

def PickUpTool1(self):
	self.execute("G53 G0 Z0")          			#Move to Z0
	self.execute("G53 G0 X11.825 Y-25.57 Z0")   #Move to top of pocket 1
	self.execute("G53 G0 Z-1.788")              #Drop the Z into position
	self.execute("M64 P10")                     #raise Pocket 1
	self.execute("M66 P17 L3 Q5")               #wait for Pocket to raise
	self.execute("M64 P8")                      #Release Spindle
	#self.execute("M66 P13 L3 Q5")               #Wait for Spindle to release
	self.execute("G4 P1")
	self.execute("M64 P2")                      #Drop Spindle
	self.execute("M66 P9 L3 Q5")                #Wait for Spindle to drop
	self.execute("G4 P0.5")
	self.execute("M65 P8")                      #Release Rel Spindle. only needs a pulse 
	self.execute("M64 P9")                      #Lock Spindle A
	self.execute("G4 P0.5")                     #wait to release pulse on lock spindle
	self.execute("M65 P9")                      #release Lock Spindle A, only needs pulse
	#self.execute("M66 P12 L3 Q5")               #Wait for spindle Has Tool 1
	self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
	self.execute("G4 P0.5")   
	self.execute("G53 G0 X15.375")   			#Move out to front of pocket 1
	self.execute("G4 P1.0")   
	self.execute("M64 P5")                      #Raise Spindle
	self.execute("M66 P7 L3 Q2")                #Wait for Spindle to raise
	self.execute("G53 G0 Z0")   				#Move to Z0
	self.execute("M65 P5")                      #RAise spindle release only pulse needed   
	self.execute("M65 P10")                     #Lower Pocket 1
	self.execute("G53 G0 Z0")                   #Move to Z0
	#INTERP_EXECUTE_FINISH
	

    
    

def PickUpTool2(self):
	self.execute("G53 G0 Z0")   				#Move to Z0
	self.execute("G53 G0 X11.900 Y-33.537 Z0")   #Move to top of pocket 2
	self.execute("G53 G0 Z-1.840")              #Drop the Z into position
	self.execute("M64 P11")                     #raise Pocket 2
	self.execute("M66 P18 L3 Q5")               #wait for Pocket to raise
	self.execute("M64 P8")                      #Release Spindle
	#self.execute("M66 P13 L3 Q5")               #Wait for Spindle to release
	self.execute("G4 P1")
	self.execute("M64 P2")                      #Drop Spindle
	self.execute("M66 P9 L3 Q5")                #Wait for Spindle to drop
	self.execute("G4 P0.5")
	self.execute("M65 P8")                      #Release Rel Spindle. only needs a pulse 
	self.execute("M64 P9")                      #Lock Spindle A
	self.execute("G4 P0.5")                     #wait to release pulse on lock spindle
	self.execute("M65 P9")                      #release Lock Spindle A, only needs pulse
	#self.execute("M66 P12 L3 Q5")               #Wait for spindle Has Tool 1
	self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
	self.execute("G4 P0.5")   
	self.execute("G53 G0 X15.375")   			#Move out to front of pocket 2
	self.execute("G4 P1.0")   
	self.execute("M64 P5")                      #Raise Spindle
	self.execute("M66 P7 L3 Q2")                #Wait for Spindle to raise
	self.execute("G53 G0 Z0")   				#Move to Z0
	self.execute("M65 P5")                      #RAise spindle release only pulse needed   
	self.execute("M65 P11")                     #Lower Pocket 2
	self.execute("G53 G0 Z0")                   #Move to Z0
	#INTERP_EXECUTE_FINISH
	

def PickUpTool3(self):
	self.execute("G53 G0 Z0")   				#Move to Z0
	self.execute("G53 G0 X11.825 Y-41.545 Z0")   #Move to top of pocket 3
	self.execute("G53 G0 Z-1.790")              #Drop the Z into position
	self.execute("M64 P12")                     #raise Pocket 3
	self.execute("M66 P19 L3 Q5")               #wait for Pocket to raise
	self.execute("M64 P8")                      #Release Spindle
	#self.execute("M66 P13 L3 Q5")               #Wait for Spindle to release
	self.execute("G4 P1")
	self.execute("M64 P2")                      #Drop Spindle
	self.execute("M66 P9 L3 Q5")                #Wait for Spindle to drop
	self.execute("G4 P0.5")
	self.execute("M65 P8")                      #Release Rel Spindle. only needs a pulse 
	self.execute("M64 P9")                      #Lock Spindle A
	self.execute("G4 P0.5")                     #wait to release pulse on lock spindle
	self.execute("M65 P9")                      #release Lock Spindle A, only needs pulse
	#self.execute("M66 P12 L3 Q5")               #Wait for spindle Has Tool 3
	self.execute("M65 P2")                      #Release drop SP relay, only needs pulse
	self.execute("G4 P0.5")   
	self.execute("G53 G0 X15.375")   			#Move out to front of pocket 3
	self.execute("G4 P1.0")   
	self.execute("M64 P5")                      #Raise Spindle
	self.execute("M66 P7 L3 Q2")                #Wait for Spindle to raise
	self.execute("G53 G0 Z0")   				#Move to Z0
	self.execute("M65 P5")                      #RAise spindle release only pulse needed   
	self.execute("M65 P12")                     #Lower Pocket 3
	self.execute("G53 G0 Z0")                   #Move to Z0
	#INTERP_EXECUTE_FINISH


#---------------------------------------------------------------------


def raisespindlesABC(self):
    #Raising Spindle A, B, C
    self.execute("M64 P5")
    self.execute("M64 P6")
    self.execute("M64 P7")
    self.execute("G4 P1.0")
    self.execute("M65 P5") 
    self.execute("M65 P6")
    self.execute("M65 P7")
    #------------------------------
    # loop through all drills
    #------------------------------
    for i in range(1, 34, 1):
        self.execute("M65 P%d" % (int(i) + 15))
    #------------------------------
    # loop through all side drills
    #------------------------------
    for i in range(1, 6, 1):
        self.execute("M65 P%d" % (int(i) + 48))
       
    
    

def CloseCasket(self):
    #----------------------------------------------------------------
    self.execute("M64 P1", lineno())
    self.execute("G4 P0.5", lineno())
    self.execute("M65 P1", lineno())
    
#----------------------------------------------------------
#----------------------------------------------------------
def OpenCasket(self):
    #----------------------------------------------------------------
    self.execute("M64 P0", lineno())
    self.execute("G4 P0.5", lineno())
    self.execute("M65 P0", lineno())
    self.execute("M66 P2 L3 Q5", lineno())
   

#----------------------------------------------------------
#------------------------------------------------------------------------------------------        
#----------------------------------------------------------
def CheckDIN(self, sWhich, doPoll):
    index = self.x.getSignalInfos(sWhich)

    if doPoll:
        self.stat.poll()
    return(int(self.stat.din[index]))
    
#----------------------------------------------------------
#----------------------------------------------------------
def CheckDOUT(self, sWhich, doPoll):
    index = self.x.getSignalInfos(sWhich)
    if doPoll:
        self.stat.poll()

    #print("signal:%s index= %d" %(sWhich, index))
    return(int(self.stat.dout[index]))

    

#----------------------------------------------------------
#----------------------------------------------------------
def SendDOUT(self, sWhich, val):
    index = self.x.getSignalInfos(sWhich)
    # only call M6x if not already at desired value
    if CheckDOUT(self, sWhich, True) != val:
        self.execute("M6%d P%d" % (4 if val == 1 else 5, index),lineno())

#----------------------------------------------------------
#----------------------------------------------------------
def WaitOnSignalToBecome(self, sWhich, val, sSec): # val = 0 (L2) val = 1 (L1)
    index = self.x.getSignalInfos(sWhich)
    self.execute("M66 P%d L%d Q%f" % (index, 4 if val == 0 else 3, sSec), lineno())
                       
#----------------------------------------------------------
#----------------------------------------------------------
def WaitAFewSeconds(self, sSec):
    self.execute("G4 P%f" % sSec, lineno())
                    
#-------------------------------------------------------------------
# M5 command to stop the spindle, here to clean up Spindle class, 
# not in moves so we don't give moves to spindle class ...
#-------------------------------------------------------------------
def StopSpindleNow(self):
    self.execute("M5", lineno())
    # Now lets stop the drill spindle if running
    self.execute("M65 P54")
    # Wait for signal spindleHasStopped to go high
    index = self.x.getSignalInfos("spindleHasStopped")
    delay = self.x.getDelay("spindlehasstopped")
    #self.execute("M66 P%d  L3 Q%f"" % (index, delay), lineno())
    self.execute("M66 P8 L3 Q15")
    print("Stop Spindle command sent")
    
	

        
        
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#   
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

#----------------------------------------------------------
#----------------------------------------------------------
def MoveZtoZero(self):
    self.execute("G53 G0 Z0.0",lineno())
    print("Moved to Z = 0.0")
    

#----------------------------------------------------------
def SetToolOffsets(self):
    self.execute("G43")
#----------------------------------------------------------

#----------------------------------------------------------
#----------------------------------------------------------
def isSpindleReallyStopped(self):
    isSpindleStopped = CheckDIN(self, "spindleHasStopped", True)
    print("isSpindleStopped = %s" % isSpindleStopped)
    if isSpindleStopped == 1:
        return True
    else:
        return False

#----------------------------------------------------------
# raising all spindles ... to make sure they are all raised
#----------------------------------------------------------
def raiseALLspindles(self):
    #------------------------------
    # loop through all spindles
    #------------------------------
    #------------------------------------------------
    # check first if all spindle are already up
    #------------------------------------------------
    print("raiseALLspindles")
    isSpindleALLup = CheckDIN(self, "spindleALLup", True)
    if isSpindleALLup == 0:
        # nope some are down, so put them all up
        validSpindle = ("A", "B", "C")
        for i in validSpindle:
            RaiseSpindleNoCheck(self, i)
    WaitOnSignalToBecome(self, "spindleALLup", self.HIGH, self.x.getDelay("spindleALLup"))
    isSpindleALLup = CheckDIN(self, "spindleALLup", True)
    if isSpindleALLup == 0:
        print("ERROR: SpindleAllup not true") #we have an error
    #------------------------------
    # loop through all drills
    #------------------------------
    for i in range(1, 34, 1):
        RaiseDrill(self, i)
    #------------------------------
    # loop through all side drills
    #------------------------------
    for i in range(1, 11, 2):
        RaiseSideDrill(self, i)
    print("All spindles, drills, and side drills are raised")
    
#----------------------------------------------------------
#----------------------------------------------------------


def DropSpindleB(self):
    index = self.x.getSignalInfos("spindleBdrop")
    self.execute("M64 P%d" % index)
    self.execute("G4 P0.5")
    self.execute("M65 P%d" % index)
    index = self.x.getSignalInfos("spindleBdown")
    self.execute("M66 P%d L4 Q1" % index)
    #self.execute("M64 P3")
    #self.execute("G4 P0.5")
    #self.execute("M65 P3")
    #self.execute("M66 P10 L4 Q1")
    print("DropSpindle(B) done")
    

def DropSpindleC(self):
    self.execute("M64 P4")
    self.execute("G4 P0.5")
    self.execute("M65 P4")
    self.execute("M66 P11 L4 Q1")
    print("DropSpindle(C) done")
    
#----------------------------------------------------------

#----------------------------------------------------------
def EnergiseSpindle(self, sWhich):
    #------------------------------
    # Deenergise if not selected
    #------------------------------
    if sWhich != "A":
        self.execute("M65 P13")
    if sWhich != "B":
        self.execute("M65 P14")
    if sWhich != "C":
        self.execute("M65 P15")
        
    #------------------------------
    # Energise if selected
    #------------------------------
    if sWhich == "A":
        self.execute("M64 P13")
    elif sWhich == "B":
        self.execute("M64 P14")
    elif sWhich == "C":
        self.execute("M64 P15")
    #------------------------------
    # wait a second
    #------------------------------
    self.execute("G4 P1.0")
    print("EnergiseSpindle(%s) done" % sWhich)
    
    #self.execute("M64 P13")
    #self.execute("M65 P14")
    #self.execute("M65 P15")
    #self.execute("G4 P1.0")

    
#----------------------------------------------------------
#----------------------------------------------------------
def DeEnergiseALLSpindle(self):
    self.execute("M65 P13") 
    self.execute("M65 P14")
    self.execute("M65 P15")
    self.execute("G4 P1.0")
    print("DeEnergiseALLSpindle done")
    
    
#----------------------------------------------------------
#----------------------------------------------------------
#----------------------------------------------------------
#----------------------------------------------------------
def SpindleHasTool(self, sWhich):
    doesSpindleHasTool = CheckDIN(self, "spindle%shastool" % sWhich, True)
    if doesSpindleHasTool == 0:
        print("Spindle has no tool")
        return False
    else:
        print("Spindle has tool")
        return True
            
#-------------------------------------------------------------------------------------------
#----------------------------------------------------------
def DropDrill(self, sWhich):
    
    index = self.x.getSignalInfos("spindle%ddrop" % sWhich)
    self.execute("M64 P%d" % (index))
    self.execute("M64 P54")
    print("DropDrill(%s) done" % sWhich)
    

#----------------------------------------------------------
#----------------------------------------------------------
def RaiseDrill(self, sWhich):
    index = self.x.getSignalInfos("spindle%ddrop" % sWhich)
    self.execute("M65 P%d" % (index)) 
    print("RaiseDrill(%s) done" % sWhich)
    

#-------------------------------------------------------------------------------------------
##----------------------------------------------------------
def DropSideDrill(self, sWhich):
    index = self.x.getSignalInfos("spindle%dand%ddrop" % (int(sWhich), int(sWhich) + 1))
    self.execute("M64 P%d" % (index)) 
    print("DropSideDrill(%s) done" % sWhich)
    
    
#----------------------------------------------------------
#----------------------------------------------------------
def RaiseSideDrill(self, sWhich):
    index = self.x.getSignalInfos("spindle%dand%ddrop" % (int(sWhich), int(sWhich) + 1))
    self.execute("M65 P%d" % (index)) 
    print("RaiseSideDrill(%s) done" % sWhich)
    
    
#-------------------------------------------------------------------------------------------
#----------------------------------------------------------
def DropTools(self, sWhich):
    drillList, sidedrillList = self.x.getMultiToolsLists(sWhich)
    # drop the drills found
    for d in drillList:
        DropDrill(self, d)
    # drop the side drills found
    for d in sidedrillList:
        DropSideDrill(self, d)
    print("DropTools(%s) done" % sWhich)
    
#----------------------------------------------------------
#----------------------------------------------------------
def FindFreePocket(self):
    #----------------------------------------------------------------
    # for each pocket defined, check if it has a tool
    #   if pocket does not have a tool, return that pocket number
    #----------------------------------------------------------------
    #---------------------------------
    # Query stat digital input status 
    #---------------------------------
    pocket1hastool = CheckDIN(self, "pocket1hastool", True)
    pocket2hastool = CheckDIN(self, "pocket2hastool", True)
    pocket3hastool = CheckDIN(self, "pocket3hastool", True)
    print("%s - %s - %s" % (pocket1hastool, pocket2hastool, pocket3hastool))
    if pocket1hastool == 1:
        if pocket2hastool == 1:
            if pocket3hastool == 1:
                return -1 # all pockets have something
            else:
                return 3    # pocket 3 has no tool
        else:
            return 2        # pocket 2 has no tool
    else:
        return 1            # pocket 1 has no tool
         
#----------------------------------------------------------
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
def DoYield():
    print("In DoYield()")
    
#---------------------------------------------------------------------------------------
# ReturnOK()
#---------------------------------------------------------------------------------------
def ReturnOK():
    print("Calling DoYield()")
    DoYield()
    print("After DoYield(), before return INTERP_OK")
    return INTERP_OK
#---------------------------------------------------------------------------------------
# ReturnERROR()
#---------------------------------------------------------------------------------------
def ReturnERROR():
    # if DoYield() is needed but I think not
    #DoYield()
    print("Before return INTERP_ERROR")
    return INTERP_ERROR
        
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
# emc_status(actualtask)
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
# return tuple (task mode, task state, exec state, interp state) as strings
#self.stat.poll()
#task_mode = ['invalid', 'MANUAL', 'AUTO', 'MDI'][self.s.task_mode]
#task_state = ['invalid', 'ESTOP', 'ESTOP_RESET', 'OFF', 'ON'][self.s.task_state]
#exec_state = ['invalid', 'ERROR', 'DONE',
#       'WAITING_FOR_MOTION',
#       'WAITING_FOR_MOTION_QUEUE',
#       'WAITING_FOR_IO',
#       'WAITING_FOR_PAUSE',
#       'WAITING_FOR_MOTION_AND_IO',
#       'WAITING_FOR_DELAY',
#       'WAITING_FOR_SYSTEM_CMD' ][self.s.exec_state]
#interp_state = ['invalid', 'IDLE', 'READING', 'PAUSED', 'WAITING'][self.s.interp_state]
#---------------------------------------------------------------------------------------
def emc_status(actualtask):
    s = linuxcnc.stat()
    s.poll()
    task_mode = s.task_mode
    task_state = s.task_state
    exec_state = s.exec_state
    interp_state = s.interp_state
    #actualtask = self.task
    
    sReturn = "---------------------------------------------------------\n"
    sReturn += "task_mode values are :\n"
    sReturn += "MODE_MANUAL : %d \n" % (linuxcnc.MODE_MANUAL)
    sReturn += "MODE_AUTO : %d \n" % (linuxcnc.MODE_AUTO)
    sReturn += "MODE_MDI : %d \n" % (linuxcnc.MODE_MDI)
    sReturn += "task_mode = %d \n" % (task_mode)
    sReturn += "\n"
    sReturn += "task_state values are :\n"
    sReturn += "STATE_ESTOP : %d \n" % (linuxcnc.STATE_ESTOP)
    sReturn += "STATE_ESTOP_RESET : %d \n" % (linuxcnc.STATE_ESTOP_RESET)
    sReturn += "STATE_OFF : %d \n" % (linuxcnc.STATE_OFF)
    sReturn += "STATE_ON : %d \n" % (linuxcnc.STATE_ON)
    sReturn += "task_state = %d \n" % (task_state)
    sReturn += "\n"
    sReturn += "exec_state values are :\n"
    sReturn += "EXEC_ERROR : %d \n" % (linuxcnc.EXEC_ERROR)
    sReturn += "EXEC_DONE : %d \n" % (linuxcnc.EXEC_DONE)
    sReturn += "EXEC_WAITING_FOR_MOTION : %d \n" % (linuxcnc.EXEC_WAITING_FOR_MOTION)
    sReturn += "EXEC_WAITING_FOR_MOTION_QUEUE : %d \n" % (linuxcnc.EXEC_WAITING_FOR_MOTION_QUEUE)
    sReturn += "EXEC_WAITING_FOR_IO : %d \n" % (linuxcnc.EXEC_WAITING_FOR_IO)
    #sReturn += "EXEC_WAITING_FOR_PAUSE : %d \n" % (linuxcnc.EXEC_WAITING_FOR_PAUSE) This does not exist
    sReturn += "EXEC_WAITING_FOR_MOTION_AND_IO : %d \n" % (linuxcnc.EXEC_WAITING_FOR_MOTION_AND_IO)
    sReturn += "EXEC_WAITING_FOR_DELAY : %d \n" % (linuxcnc.EXEC_WAITING_FOR_DELAY)
    sReturn += "EXEC_WAITING_FOR_SYSTEM_CMD : %d \n" % (linuxcnc.EXEC_WAITING_FOR_SYSTEM_CMD)
    sReturn += "exec_state = %d \n" % (exec_state)
    sReturn += "\n"
    sReturn += "interp_state values are :\n"
    sReturn += "INTERP_IDLE : %d \n" % (linuxcnc.INTERP_IDLE)
    sReturn += "INTERP_READING : %d \n" % (linuxcnc.INTERP_READING)
    sReturn += "INTERP_PAUSED : %d \n" % (linuxcnc.INTERP_PAUSED)
    sReturn += "INTERP_WAITING : %d \n" % (linuxcnc.INTERP_WAITING)
    sReturn += "interp_state = %d \n" % (interp_state)
    sReturn += "\n"
    sReturn += "self.task = %d\n" % (actualtask)
    sReturn += "---------------------------------------------------------\n"

    return sReturn #(task_mode, task_state, exec_state, interp_state)
