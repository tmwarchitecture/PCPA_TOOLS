import rhinoscriptsyntax as rs
import Rhino
import datetime

def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)

def importCAD(savePath0, CADinMilli):
    explodeBlockBoo = True
    
    #setup the layers
    rs.AddLayer("7_REF")
    rs.AddLayer("CAD", parent = "7_REF")
    
    fileNameExt = savePath0.split('\\')[-1]
    fileName = fileNameExt.split('.')[0]
    savePath1 = '"'+savePath0+'"'
    
    #create layer name
    now = datetime.date.today()
    dateList = []
    if len(str(now.month))>1:
        month = str(now.month)
    else:
        month = "0"+str(now.month)
    if len(str(now.day))>1:
        day = str(now.day)
    else:
        day = "0"+str(now.day)
    time = str(now.year)+month+day
    layerName = time+"_"+fileName+"_01"
    children = rs.LayerChildren("7_REF::CAD")
    finalNums = []
    for child in children:
        num = rs.LayerName(child, fullpath = False).split("_")[-1]
        try:
            finalNums.append(int(num))
        except:
            finalNums.append(0)
    finalNums.sort()
    if rs.IsLayer("7_REF::CAD::"+layerName):
        num = int(finalNums[-1])+1
        if len(str(num))<2:
            finalNum = "0" + str(num)
        else:
            finalNum = str(num)
        layerName = time+"_"+fileName+ "_" + finalNum
    par = rs.AddLayer("7_REF")
    cat = rs.AddLayer("CAD", parent = par)
    element = rs.AddLayer(layerName, parent = cat)
    rs.CurrentLayer(element)
    
    #get intial list of all layers in the file
    currentLayers = rs.LayerNames()
    
    rs.Command('_-Import '+savePath1+' _Enter')
    
    #get new layers added
    endLayersNames = rs.LayerNames()
    #newLayers = [item for item in currentLayers if item not in endLayersNames]
    newLayers = diff(endLayersNames, currentLayers)
    
    for layer in newLayers:
        rs.ParentLayer(layer, element)
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
    for finalLayer in finalLayers:
        allObjects.append(rs.ObjectsByLayer(finalLayer))
    finalAllObjects = [item for sublist in allObjects for item in sublist]
    
    
    if CADinMilli:
        rs.ScaleObjects(finalAllObjects, [0,0,0], [.001, .001, .001])
    
    importGroup = rs.AddGroup(str(layerName))
    
    rs.AddObjectsToGroup(finalAllObjects, importGroup)
    
    print "Import EXECUTED"
    return finalAllObjects

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

def  main():
    #Import CAD
    filePath = rs.OpenFileName("Open", "Autocad (*.dwg)|*.dwg||")
    if filePath is None: return
    
    itemsMM = [ ["Units", "Meters", "Millimeters"] ]
    CADinMilli = rs.GetBoolean("Is that CAD file in meters or mm?", itemsMM, [True])[0]
    CADinMilli = False
    
    originItems = ("Use_CAD_Origin", "No", "Yes")
    useOrigin = rs.GetBoolean("Use CAD Coordinate?", originItems, (True))[0]
    useOrigin = False
    
    rs.EnableRedraw(False)
    allImportedObjects = importCAD(filePath, CADinMilli)
    if useOrigin:
        moveToOrigin(allImportedObjects, CADinMilli)
    rs.ZoomSelected()
    rs.EnableRedraw(True)

main()