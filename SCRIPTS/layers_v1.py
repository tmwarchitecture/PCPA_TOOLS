import rhinoscriptsyntax as rs
import Rhino
import os
import scriptcontext as sc

from libs import csv

import config
import utils

__author__ = 'Tim Williams'
__version__ = "2.1.0"

#Utils
def setupVariables():
    fileLocations = config.GetDict()
    global csvPath
    csvPath = fileLocations['PCPA Layers_V1']


    global layNumColumn
    layNumColumn = 0
    global nameColumn
    nameColumn = 1
    global parentColumn
    parentColumn = 2
    global colorColumn
    colorColumn = 3
    global materialColumn
    materialColumn = 4
    global linetypeColumn
    linetypeColumn = 5
    global printcolorColumn
    printcolorColumn = 6
    global printwidthColumn
    printwidthColumn = 7
    global fullLayerNameColumn
    fullLayerNameColumn = 8
#############################################################

#Layers
def MaterialToLayer(layer, matName):
    def loadMatFromPath(path):
        if os.path.isfile(path):
            rdk = rs.GetPlugInObject("Renderer Development Kit")
            rc = rdk.ContentLoadFromFile(path)
            return rc
        else: return None

    def ApplyMaterialToLayer(material, layer):
        matName = '"' + str(material) + '"'
        layName = '"' + layer + '"'
        rs.Command("-_RenderAssignMaterialToLayer " + str(matName) + " " + str(layName) + " ", False)

    def getMaterialNames():
        rdk = rs.GetPlugInObject("Renderer Development Kit")
        rdkALL = rdk.FactoryList()
        arrMatIDList = rdk.ContentList("material")
        arrMatNames = []
        try:
            len(arrMatIDList)
        except:
            return None
        for i in range(len(arrMatIDList)):
            arrMatNames.append(rdk.ContentInstanceName(arrMatIDList[i]))
        return arrMatNames

    def IsMaterial(materialName):
        matNames = getMaterialNames()
        if matNames is None: return False
        for name in matNames:
            if name == materialName:
                return True
        return False

    def ForceMaterialToLayer(materialName, mylayer):
        """
        Applies material by name to layer. If no layer found, it is imported.
            materialName: str
            mylayer: str
        """
        fileLocations = config.GetDict()
        materialNameFull = materialName + '.rmtl'
        dir = fileLocations['Material Folder']
        matpath = os.path.join(dir, materialNameFull)
        if IsMaterial(materialName):
            ApplyMaterialToLayer(materialName, mylayer)
        else:
            result = loadMatFromPath(matpath)
            if result is None:
                print "Material {} not found".format(materialName)
            else:
                ApplyMaterialToLayer(materialName, mylayer)

    if len(matName) < 1:
        return
    ForceMaterialToLayer(matName, layer)

def GetChildNumbers(parentNum, layerData):
    numsInCSV = list(layerData.keys())
    if parentNum == 10000:
        nums = range(0, parentNum)
        return list(set(numsInCSV) & set(nums))
    elif parentNum%1000 == 0:
        nums = range(parentNum, parentNum+1000)
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

    data = AddLayerFullName(data)

    return data

def AddLayerFullName(data):
    for eachRow in data:
        fullName = []
        counter = 0
        def getShortName(number, fullName, counter):
            counter += 1
            if counter > 5:
                print "Loop detected"
                return

            shortName = data[number][nameColumn]
            try:
                #Has a parent layer
                parentNum = int(data[number][parentColumn])
                fullName.append(shortName)
                fullName.append('::')
                fullName = getShortName(parentNum, fullName, counter)
            except:
                #No parent layer
                fullName.append(shortName)
            return fullName

        fullName = getShortName(eachRow, fullName, counter)
        fullName.reverse()
        fullNameString = "".join(fullName)
        data[eachRow].append(fullNameString)
        global fullLayerNameColumn
        fullLayerNameColumn = len(data[eachRow])-1
        #print data[eachRow]
    return data

def translateColor(dashColor):
    if len(dashColor) < 1: return [0,0,0]
    try:
        color = [int(x) for x in dashColor.split("-")]
    except:
        color = None
    return color

def AddLayers(layerData, layerNumbers):
    counter = 0
    rootLayers = []

    def AddThisLayer(thisLayerData, counter):
        ##########################
        isRoot = False
        try:
            counter += 1
            if counter > 4:
                print "Loooop detected"
                return
            int(thisLayerData[parentColumn])
            parentLayData = layerData[thisLayerData[parentColumn]]
            parentLay = AddThisLayer(parentLayData, counter)
        except:
            isRoot = True
            parentLay = None
        ##########################
        if rs.IsLayer(thisLayerData[fullLayerNameColumn]):
            rootLayers.append(thisLayerData[fullLayerNameColumn])

            return thisLayerData[fullLayerNameColumn]
        newLayer = rs.AddLayer(thisLayerData[fullLayerNameColumn], thisLayerData[colorColumn])
        rs.LayerLinetype(newLayer, thisLayerData[linetypeColumn])
        rs.LayerPrintColor(newLayer, thisLayerData[printcolorColumn])
        rs.LayerPrintWidth(newLayer, thisLayerData[printwidthColumn])
        try:
            MaterialToLayer(newLayer, thisLayerData[materialColumn])
        except:
            print "Material failed"
            #pass

        if isRoot:
            rootLayers.append(newLayer)
        return newLayer

    for layerNumber in layerNumbers:
        try:
            thisLayer = layerData[layerNumber]
            AddThisLayer(thisLayer, counter)

        except:
            pass
    return list(set(rootLayers))

def CollapseRootLayers(roots):
    rs.EnableRedraw(False)
    for root in roots:
        try:
            rootLay = sc.doc.Layers.FindId(rs.coerceguid(rs.LayerId(root)))
            rootLay.IsExpanded = False
        except:
            pass
    rs.EnableRedraw(True)

def AddSpecificLayer(layerNumRequested, collapse = True):
    """
    AddSpecificLayer(layerNumRequested, collapse = True)
    """
    print "AddSpecificLayer is obsolete"
    setupVariables()
    rs.EnableRedraw(False)
    if layerNumRequested is None: return

    global csvPath
    layerData = GetLayerData(csvPath)

    layerNums = GetChildNumbers(layerNumRequested, layerData)
    layerNums.sort()

    roots = AddLayers(layerData, layerNums)

    if collapse:
        CollapseRootLayers(roots)
    rs.EnableRedraw(True)
    return roots

def AddLayerByNumber(layerNumRequested, collapse = True):
    """
    AddSpecificLayer(layerNumRequested, collapse = True)
    """
    setupVariables()
    rs.EnableRedraw(False)
    if layerNumRequested is None: return

    global csvPath
    layerData = GetLayerData(csvPath)

    layerNums = GetChildNumbers(layerNumRequested, layerData)
    layerNums.sort()

    roots = AddLayers(layerData, layerNums)

    if collapse:
        CollapseRootLayers(roots)
    rs.EnableRedraw(True)
    return roots


#############################################################

def GetLayerFullName(layerData, layerNumbers):
    def GetThisLayer(thisLayerData, counter, thisLayersName):
        ##########################
        isRoot = False
        try:
            counter += 1
            if counter > 4:
                print "Loooop detected"
                return
            int(thisLayerData[parentColumn]) #test if has parent
            parentLayData = layerData[thisLayerData[parentColumn]]
            thisLayersName = parentLayData[nameColumn] + "::" + thisLayersName
            thisLayersName = GetThisLayer(parentLayData, counter, thisLayersName)
        except:
            isRoot = True
            parentLay = None
        ##########################
        return thisLayersName

    counter = 0
    rootLayers = []
    allNames = []

    for layerNumber in layerNumbers:
        try:
            thisLayer = layerData[layerNumber]
            thisName = thisLayer[nameColumn]
            allNames.append(GetThisLayer(thisLayer, counter, thisName))
        except:
            pass
    return allNames

def GetLayerNameByNumber(layerNumRequested):
    if layerNumRequested is None: return

    setupVariables()

    layerData = GetLayerData(csvPath)

    try:
        layers = GetLayerFullName(layerData, [layerNumRequested])[0]
    except:
        layers = GetLayerFullName(layerData, [layerNumRequested])

    return layers

def GetAllLayerNames():
    allLayerNames = []
    layerNums = []

    setupVariables()

    global csvPath
    layerData = GetLayerData(csvPath)
    for i in range(0,10000,1000):
        layerNumsSet = GetChildNumbers(i, layerData)
        layerNumsSet.sort()
        layerNums = layerNums + layerNumsSet

    for each in layerNums:
        allLayerNames.append(GetLayerNameByNumber(each))
    return allLayerNames

if __name__ == "__main__":
    setupVariables()
    layerNumRequested = rs.GetInteger("Enter layer number to add to the document", number = 10000, minimum = 0, maximum = 10000)
    AddLayerByNumber(layerNumRequested)
    utils.SaveToAnalytics('layers_v1-'+str(layerNumRequested))
    #print GetLayerNameByNumber(layerNumRequested)
