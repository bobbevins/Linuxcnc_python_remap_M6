#!/usr/bin/env python
#------------------------------------------------------------------------------------------------
import xml.etree.ElementTree as oXML


# have to add error handling here when fields are not found ...





class xmlBiesse(object):
    
    def __init__(self, x):
        self.oXMLtree = oXML.parse(x)
        self.oXMLroot = self.oXMLtree.getroot()
        self.drillOffset = 400
        self.sidedrillOffset = 500
        
        # print the machine type for the XML
        machineType = self.oXMLroot.get('type')
        print("# Machine type is : %s" % machineType)
        
    #--------------------------------------------------------------------------    
    # for Signals/Signal name= returns index, dir, isPulse, mesanet in a tuple
    #--------------------------------------------------------------------------    
    def getSignalInfos(self, sSignalName):
        #print("Signal Name : %s" % sSignalName)
        oXML = self.oXMLroot.find('Signals/Signal[@name="%s"]' %  sSignalName) 
        #print(oXML)
        if oXML == None:
            #print("Special Button")
            oXML = self.oXMLroot.find('SpecialButtons/OR2[@name="%s"]' %  sSignalName) 
            if oXML == None:
                raise ValueError("did not found the special button in the xml: %s" % sSignalName)
        index = oXML.get('index')
        return int(index)
        
    #--------------------------------------------------------------------------    
    # for ALL Delays, time to wait to ..
    #--------------------------------------------------------------------------    
    def getDelay(self, sDelayName):
        oXML = self.oXMLroot.find('Delays/Delay[@name="%s"]' %  sDelayName) 
        val = oXML.get('val')
        return float(val) 

    #--------------------------------------------------------------------------    
    # For Feed speed
    #--------------------------------------------------------------------------    
    def getFeedSpeed(self):
        oXML = self.oXMLroot.find('Feed') 
        feedSpeed = oXML.get('speed')
        return int("%s" % feedSpeed)
        
    #--------------------------------------------------------------------------    
    # get the position of the pocket ... 1,2,3 and Top or Front
    #--------------------------------------------------------------------------    
    def getPocketPos(self, sWhichPocket, sWhichPosition):
        #print("%s-%s" % (sWhichPocket, sWhichPosition))
        oXML = self.oXMLroot.find('Pockets/Pocket[@id="%s"]' % sWhichPocket)
        oXML2 = oXML.find('%s' % sWhichPosition)
        posX = oXML2.get("x")
        posY = oXML2.get("y")
        posZ = oXML2.get("z")
        return float(posX), float(posY), float(posZ)
    
    def getMultiToolsLists(self, sWhich700Tool):
        drillList = []
        sidedrillList = []
        # Fetch the tool definition in the xml
        oXML = self.oXMLroot.find('SpecialTools/ToolSeries[@id="%s"]' % sWhich700Tool) 
        
        # error handling .. if not found ... raise error to caller ...
        
        
        # get the drills
        countDrills = 0
        for x in oXML.iter("Drill"):
            drillID = int(x.get("id"))
            print("%d" % drillID)
            countDrills += 1
            drillList.append(drillID - self.drillOffset)
        # get the side drills
        countSideDrills = 0
        for x in oXML.iter("SideDrill"):
            sidedrillID = int(x.get("id"))
            print("%d" % sidedrillID)
            countSideDrills += 1
            sidedrillList.append(sidedrillID - self.sidedrillOffset)
        print("Drills: %d, Side Drills: %d" % (countDrills, countSideDrills))
        # return the two lists
        return drillList, sidedrillList
