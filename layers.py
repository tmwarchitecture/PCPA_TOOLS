import rhinoscriptsyntax as rs
import Rhino
import os
import scriptcontext as sc

from libs import csv

filename = "PCPA LAYERS_V1.csv"
dataDir = "data"
root = os.path.dirname(os.path.realpath(__file__))
csvPath = os.path.join(root,dataDir, filename)

PCPA_Layers = csvPath

layNumColumn = 0
nameColumn = 1
parentColumn = 2
colorColumn = 3
materialColumn = 4
linetypeColumn = 5
printcolorColumn = 6
printwidthColumn = 7

#sc.doc.Materials.FindIndex(
#print "HERE: " + str(Rhino.DocObjects.Tables.MaterialTable.CurrentMaterialIndex)
def GetChildNumbers(parentNum, layerData):
    numsInCSV = list(layerData.keys())
    if parentNum == 10000:
        nums = range(0, parentNum)
        return list(set(numsInCSV) & set(nums))
    elif parentNum%1000 == 0:
        nums = range(parentNum+1, parentNum+1000)
        return list(set(numsInCSV) & set(nums))
    elif parentNum%100 == 0:
        nums = range(parentNum+1, parentNum+100)
        return list(set(numsInCSV) & set(nums))
    else:
        return [parentNum]

def GetLayerData(fileName):
    with open(fileName, 'rb') as f:
        reader = csv.reader(f)
        layerData = list(reader)
    
    #Delete non-number layers
    newList = []
    for i, row in enumerate(layerData):
        try:
            int(row[layNumColumn])
            newList.append(row)
        except:
            pass
    
    data = {}
    for row in newList:
        try:
            printwidth = float(row[printwidthColumn])
        except:
            printwidth = 0
        try:
            parentcol = int(row[parentColumn])
        except:
            parentcol = row[parentColumn]
        data[int(row[layNumColumn])] = [int(row[layNumColumn]), row[nameColumn],
        parentcol, translateColor(row[colorColumn]), row[materialColumn], 
        row[linetypeColumn], translateColor(row[printcolorColumn]), printwidth]
    return data

def translateColor(dashColor):
    if len(dashColor) < 1: return [0,0,0]
    return [int(x) for x in dashColor.split("-")]

def AddLayers(layerData, layerNumbers):
    counter = 0
    def AddThisLayer(thisLayerData, counter):
        ##########################
        try:
            counter += 1
            if counter > 4:
                print "Looop detected"
                return
            int(thisLayerData[parentColumn])
            parentLayData = layerData[thisLayerData[parentColumn]]
            parentLay = AddThisLayer(parentLayData, counter)
        except:
            parentLay = None
        ##########################
        newLayer = rs.AddLayer(thisLayerData[nameColumn], thisLayerData[colorColumn], parent = parentLay)
        rs.LayerLinetype(newLayer, thisLayerData[linetypeColumn])
        rs.LayerPrintColor(newLayer, thisLayerData[printcolorColumn])
        rs.LayerPrintWidth(newLayer, thisLayerData[printwidthColumn])
        return newLayer
    
    for layerNumber in layerNumbers:
        try:
            thisLayer = layerData[layerNumber]
            AddThisLayer(thisLayer, counter)
        except:
            pass

def CollapseRootLayers():
    print "Collapse"
    #print Rhino.DocObjects.Tables.LayerTable.
    #rs.coercerhinoobject(

def main():
    rs.EnableRedraw(False)
    #layerNumRequested = rs.GetInteger("Enter layer number to add to the document", number = 10000, minimum = 0, maximum = 10000)
    #if layerNumRequested is None: return
    #layerData = GetLayerData(PCPA_Layers)
    
    #layerNums = GetChildNumbers(layerNumRequested, layerData)
    
    #AddLayers(layerData, layerNums)
    
    CollapseRootLayers()
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()