import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def loadMatsFromFile(path):
    rdk = rs.GetPlugInObject("Renderer Development Kit")
    rdk.ContentLoadFromFile(path)

def AddMatToMatTable(name):
    print "ADDING {}".format(name)

def getMaterialNames():
    rdk = rs.GetPlugInObject("Renderer Development Kit")
    #get list of all RDK data ids in the document
    rdkALL = rdk.FactoryList()
    #rs.
    #filtered materials ID list
    arrMatIDList = rdk.ContentList("material") 
    #abc = Rhino.Render.RenderMaterialTable.Count
    print len(arrMatIDList)
    
    materialDict = {}
    
    #get materials names
    arrMatNames = []
    for i in range(len(arrMatIDList)):
        matTable = sc.doc.ActiveDoc.Materials
        
        #sc.doc.ActiveDoc.Materials.Add(
        
        arrMatNames.append( rdk.ContentInstanceName(arrMatIDList[i]) )
        result = rdk.SetMaterialInstanceId( arrMatIDList[i],i)
        name = rdk.ContentInstanceName(arrMatIDList[i])
        print "A"
    
    matCount = sc.doc.ActiveDoc.Materials.Count
    for i in range(matCount):
        
        x = rdk.MaterialInstanceId(i)
        
        print "A"
        name = rs.MaterialName(i)
        if name is None: continue
        
        found = False
        for matName in arrMatNames:
            if  matName == name:
                materialDict[name] = i
                found = True
                continue
        print "A"
        if not found:
            AddMatToMatTable(name)
    print materialDict
    

def test():
    
    print "A"
    #layer = rs.CurrentLayer()
    #rs.LayerMaterialIndex(layer, 0)
    
    
    #if index==-1: index = rs.AddMaterialToLayer(layer)
    #print index

path = r'C:\Users\Tim\Desktop\temp\mats\airplane.rmtl'
#loadMatsFromFile(path)
getMaterialNames()
#test()
#rs.AddMaterialToLayer(

#1 LOAD ALL MATERIALS TO RDK
#2 LOAD MATERIALS INTO MATERIAL TABLE
    #IF THEY DONT ALREADY EXIST IN THERE
#3 GET MATERIAL INDEX
#4 APPLY MATERIAL TO LAYER BY INDEX