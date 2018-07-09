import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import os.path
import layers
import block_tools
import config
from utils import GetDatePrefix

################################################################################
#Utils

def flatten(lst):
    return sum( ([x] if not isinstance(x, list) else flatten(x) for x in lst), [] )

def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)

################################################################################
#Import 2D Functions

def moveToOrigin(allObjects, CADinMilli):
    cadOrigin = rs.GetDocumentData("Project Info", "CAD coordinate (X,Y,Z)")
    cadOrigin = cadOrigin.split(",")
    try:
        moveVec = rs.VectorCreate([0,0,0],  [float(cadOrigin[0]), float(cadOrigin[1]), float(cadOrigin[2])])
    except:
        print "Move to origin FAILED. Make sure CAD Coordinate has been correctly entered into Project Info."
        return
    if CADinMilli:
        moveVec = rs.VectorScale(moveVec, .001)
    rs.MoveObjects(allObjects,moveVec)
    return

def importCAD(savePath0, CADinMilli):
    explodeBlockBoo = True
    
    #setup the layers
    importLayerObj = layers.AddSpecificLayer(6000)
    importLayerName = layers.GetLayerNames(6000)[0]
    
    #Shorten cad file name
    fileNameExt = savePath0.split('\\')[-1]
    fileName = fileNameExt.split('.')[0]
    savePath1 = '"'+savePath0+'"'
    
    #create layer name
    time = utils.GetDatePrefix()
    iter = "01"
    layerName = time+"_"+fileName+"_"+iter
    
    #Check if this layer already exists
    while rs.IsLayer(importLayerName + "::" + time + "_" + fileName + "_" + iter):
        iterInt = int(iter)+1
        if len(str(iterInt))<2:
            iter = "0" + str(iterInt)
        else:
            iter = str(iterInt)
    
    elementLayerName = importLayerName + "::" + time + "_" + fileName + "_" + iter
    elementLayer = rs.AddLayer(elementLayerName)
    
    rs.CurrentLayer(elementLayer)
    
    #get intial list of all layers in the file
    currentLayers = rs.LayerNames()
    
    rs.Command('_-Import '+savePath1+' _Enter')
    
    #get new layers added
    endLayersNames = rs.LayerNames()
    #newLayers = [item for item in currentLayers if item not in endLayersNames]
    newLayers = diff(endLayersNames, currentLayers)
    
    for layer in newLayers:
        rs.ParentLayer(layer, elementLayer)
        objects = rs.ObjectsByLayer(layer)
        if rs.IsLayerEmpty(layer):
            rs.DeleteLayer(layer)
        else:
            for obj in objects:
                if rs.IsDimension(obj):
                    rs.DeleteObject(obj)
                elif rs.IsHatch(obj):
                    rs.DeleteObject(obj)
    
    #Get all the imported geometry
    allObjects = []
    finalLayers = rs.LayerChildren(rs.CurrentLayer())
    blockNames = []
    for finalLayer in finalLayers:
        layerObjects = rs.ObjectsByLayer(finalLayer)
        for layerObject in layerObjects:
            if rs.IsBlockInstance(layerObject):
                blockNames.append(rs.BlockInstanceName(layerObject))
                allObjects.append(rs.ExplodeBlockInstance(layerObject, True))
            else:
                allObjects.append(layerObject)
    finalAllObjects = list(flatten(allObjects))
    
    for eachBlock in blockNames:
        try:
            rs.DeleteBlock(eachBlock)
        except:
            pass
    
    
    #Scale objects
    if CADinMilli:
        rs.ScaleObjects(finalAllObjects, [0,0,0], [.001, .001, .001])
    
    #importGroup = rs.AddGroup(str(layerName))
    
    #rs.AddObjectsToGroup(finalAllObjects, importGroup)
    
    #Collapse layers
    try:
        rootLay = sc.doc.Layers.FindId(rs.coerceguid(rs.LayerId(elementLayerName)))
        rootLay.IsExpanded = False
    except:
        pass
    
    print "Import EXECUTED"
    return finalAllObjects

def importDWG():
    #Import CAD
    filePath = rs.OpenFileName("Open", "Autocad (*.dwg)|*.dwg||")
    if filePath is None: return
    
    #itemsMM = [ ["Units", "Meters", "Millimeters"] ]
    #CADinMilli = rs.GetBoolean("Is that CAD file in meters or mm?", itemsMM, [True])[0]
    CADinMilli = False
    
    #originItems = ("Use_CAD_Origin", "No", "Yes")
    #useOrigin = rs.GetBoolean("Use CAD Coordinate?", originItems, (True))[0]
    useOrigin = False
    
    rs.EnableRedraw(False)
    allImportedObjects = importCAD(filePath, CADinMilli)
    if useOrigin:
        moveToOrigin(allImportedObjects, CADinMilli)
    rs.ZoomSelected()
    rs.EnableRedraw(True)

################################################################################
#Export Functions
def AddMasterRootLayer(masterRoot):
    rs.EnableRedraw(False)
    
    exceptionLayer = 'BLOCKS'
    
    parentLayers = []
    allLayers = rs.LayerNames()
    for each in allLayers:
        if rs.ParentLayer(each) is None:
            parentLayers.append(each)
    
    newLayer = rs.AddLayer(str(masterRoot))
    for eachLayer in parentLayers:
        if eachLayer == newLayer:
            pass
        elif eachLayer == exceptionLayer:
            pass
        else:
            rs.ParentLayer(eachLayer, newLayer)
    rs.EnableRedraw(True)

def RemoveMasterRootLayer(masterRoot):
    rs.EnableRedraw(False)
    
    subRoots = []
    allLayers = rs.LayerNames()
    for each in allLayers:
        if rs.ParentLayer(each) == masterRoot:
            subRoots.append(each)
    
    for eachLayer in subRoots:
        rs.ParentLayer(eachLayer, '')
    rs.DeleteLayer(masterRoot)
    rs.EnableRedraw(True)

def exportToRender():
    fileLocations = config.GetDict()
    
    print "Exporting to 3ds max"
    objs = rs.GetObjects("Select objects to export", preselect=True)
    if objs is None: return
    
    #SAVE FILE NAME
    defaultFolder = rs.DocumentPath()
    defaultFilename = GetDatePrefix() + '_OPTION_01'
    fileName = rs.SaveFileName("Export to render", "Autocad (*.dwg)|*.dwg||", defaultFolder, defaultFilename)
    if fileName is None: return
    base=os.path.basename(fileName)
    cadName = os.path.splitext(base)[0]
    
    #SUPER EXPLODE
    #EXPLODE SELECTED BLOCKS (CHECKLIST) [this is broken]
        #blockNames = rs.BlockNames(True)
        #print blockNames
        
        #results = rs.CheckListBox(blockNames, "Select blocks to explode", "Explode for render")
    #CHECK BACKFACES
    #CHECK GEOMETRY
    #EXPORT EACH LAYER AS SAT FILE.
    #CHECK ORIGIN 
    #INSERT ORIGIN
    #CHECK SCALE (Units)
    if rs.UnitSystem() == 8:
        print "Units checked"
    else:
        print "This model is in {}, it should be in Inches".format(rs.UnitSystemName(singular=False))
    #UNIFY MESH NORMALS
    #MERGE ALL EDGES
    #MERGE ALL FACES
    
    #DELETE DUPS
    #rs.UnselectAllObjects()
    #rs.Command('-_Seldup ', echo=False)
    #dupObjs = rs.SelectedObjects()
    #if len(dupObjs) > 0:
    #    rs.DeleteObjects(dupObjs)
    #    print "{} duplicate objects deleted".format(len(dupObjs))
    
    #JOIN BY LAYER
    
    #PLACE UNDER A PARENT LAYER W/ DATESTAMP
    AddMasterRootLayer(cadName)
    
    #CHANGE LAYER NAMES?
    #IMPORT ACAD SCHEME
    #SET DEFAULT FOLDER TO REFERENCE FOLDER UNDER RENDERING
    
    #EXPORT TO DWG
    rs.SelectObjects(objs)
    acadSchemeFolder = fileLocations['ACAD Scheme Folder']
    exportScheme = 'MaxSolids.ini'
    iniFile = os.path.join(acadSchemeFolder, exportScheme)
    rs.Command('-_Export ' + '"' + fileName + '" F ' + '"' + iniFile + '"' + ' Enter P 100 Enter')
    
    #REMOVE MASTER ROOT LAYER
    RemoveMasterRootLayer(cadName)

def  main():
    func = rs.GetInteger("Function to run", number = 0)
    if func == 0:
        importDWG()
    elif func == 1:
        exportToRender()

if __name__ == "__main__":
    main()