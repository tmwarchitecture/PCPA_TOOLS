import rhinoscriptsyntax as rs
import Rhino
import layers
import utils
import scriptcontext as sc
import block_tools

def flatten(lst):
    return sum( ([x] if not isinstance(x, list) else flatten(x) for x in lst), [] )

def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)

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

def  main():
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

main()