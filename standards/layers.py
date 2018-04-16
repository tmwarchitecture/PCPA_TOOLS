import rhinoscriptsyntax as rs
import csv
import Rhino
import sys
sys.path.append(r'E:\Files\Work\LIBRARY\06_RHINO\41_PCPA')
import PCPA
import imp
#csv = imp.load_source('csv', PCPA.config.GetValue('CSV'))
import scriptcontext as sc

PCPA_Layers = PCPA.tools.config.GetValue('PCPA_Layers')

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
    if parentNum%1000 == 0:
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
    for i, row in enumerate(layerData):
        try:
            int(row[layNumColumn])
        except:
            del layerData[i]
    
    data = {}
    for row in layerData:
        try:
            printwidth = float(row[printwidthColumn])
        except:
            printwidth = 0
        try:
            parentcol = int(row[parentColumn])
        except:
            parentcol = 0
        data[int(row[layNumColumn])] = [int(row[layNumColumn]), row[nameColumn],
        parentcol, translateColor(row[colorColumn]), row[materialColumn], 
        row[linetypeColumn], translateColor(row[printcolorColumn]), printwidth]
    return data

def translateColor(dashColor):
    if len(dashColor) < 1: return [0,0,0]
    return [int(x) for x in dashColor.split("-")]

def AddLayers(layerData, layerNumbers):
    def AddThisLayer(thisLayerData):
        ##########################
        try:
            parentLayData = layerData[thisLayerData[parentColumn]]
            parentLay = AddThisLayer(parentLayData)
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
            AddThisLayer(thisLayer)
        except:
            pass

def main():
    rs.EnableRedraw(False)
    layerNumRequested = rs.GetInteger("Enter layer number to add to the document", minimum = 1)
    if layerNumRequested is None: return
    
    layerData = GetLayerData(PCPA_Layers)
    layerNums = GetChildNumbers(layerNumRequested, layerData)
    
    AddLayers(layerData, layerNums)
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()