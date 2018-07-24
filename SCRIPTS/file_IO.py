import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import random
import os.path

import layers
import blocks
import config
import utils
import standards

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

def importCAD(savePath0, scaleDWG):
    explodeBlockBoo = True
    
    #setup the layers
    importLayerNumber = 6000
    importLayerObj = layers.AddLayerByNumber(importLayerNumber, False)
    importLayerName = layers.GetLayerNameByNumber(importLayerNumber)
    
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
    
    rs.Command('_-Import '+savePath1+' _Enter', False)
    
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
    if scaleDWG:
        rs.ScaleObjects(finalAllObjects, [0,0,0], [.001, .001, .001])
    
    #importGroup = rs.AddGroup(str(layerName))
    #rs.AddObjectsToGroup(finalAllObjects, importGroup)
    
    #Collapse layers
    try:
        rootLay = sc.doc.Layers.FindId(rs.coerceguid(rs.LayerId(elementLayerName)))
        rootLay.IsExpanded = False
    except:
        pass
    
    print "Import Successful"
    return finalAllObjects

def importDWG():
    try:
        #Import CAD
        filePath = rs.OpenFileName("Select CAD to Import", "Autocad (*.dwg)|*.dwg||")
        if filePath is None: return
        
        #itemsMM = [ ["Units", "Meters", "Millimeters"] ]
        #CADinMilli = rs.GetBoolean("Is that CAD file in meters or mm?", itemsMM, [True])[0]
        scaleDWG = False
        
        #originItems = ("Use_CAD_Origin", "No", "Yes")
        #useOrigin = rs.GetBoolean("Use CAD Coordinate?", originItems, (True))[0]
        useOrigin = False
        
        rs.EnableRedraw(False)
        allImportedObjects = importCAD(filePath, scaleDWG)
        #if useOrigin:
        #    moveToOrigin(allImportedObjects, scaleDWG)
        rs.ZoomSelected()
        rs.EnableRedraw(True)
        return True
    except:
        print "Import Failed"
        return False

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

def exportToRenderDWG():
    try:
        fileLocations = config.GetDict()
        
        print "Exporting to 3ds max"
        objs = rs.GetObjects("Select objects to export", preselect=True)
        if objs is None: return
        
        #SAVE FILE NAME
        defaultFolder = rs.DocumentPath()
        defaultFilename = utils.GetDatePrefix() + '_OPTION_01'
        fileName = rs.SaveFileName("Export to render", "Autocad (*.dwg)|*.dwg||", defaultFolder, defaultFilename)
        if fileName is None: return
        base=os.path.basename(fileName)
        cadName = os.path.splitext(base)[0]
        
        #SUPER EXPLODE
        #EXPLODE SELECTED BLOCKS (CHECKLIST)
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
        standards.LoadAcadSchemes(fileLocations['ACAD Scheme Folder'])
        
        #SET DEFAULT FOLDER TO REFERENCE FOLDER UNDER RENDERING
        
        #EXPORT TO DWG
        rs.SelectObjects(objs)
        exportScheme = 'PCPA_MaxSolids'
        rs.Command('-_Export ' + '"' + fileName + '" S ' + '"' + exportScheme + '"' + ' Enter P 100 Enter', False)
        
        #REMOVE MASTER ROOT LAYER
        RemoveMasterRootLayer(cadName)
        return True
    except:
        return False

def exportToRenderSKP():
    try:
        objs = rs.GetObjects("Select objects to export", preselect = True)
        if objs is None: return
        
        seperator = ' > '
        
        defaultFilename = utils.GetDatePrefix() + '_OPTION_01'
        defaultFolder = rs.DocumentPath()
        fileName = rs.SaveFileName("Export to render", "Sketchup 2015 (*.skp)|*.skp||", folder = defaultFolder, filename = defaultFilename)
        if fileName is None: return
        
        tempLayers = []
        copiedObjs = []
        
        baseName = os.path.splitext(os.path.basename(fileName))[0]
        
        #Copy all objects to export
        rs.StatusBarProgressMeterShow('Exporting to SKP', 0, len(objs))
        for i, obj in enumerate(objs):
            tempCopy = rs.CopyObject(obj)
            if rs.IsBlockInstance(tempCopy):
                explodedObjs = list(rs.ExplodeBlockInstance(obj, True))
                copiedObjs += explodedObjs
            else:
                copiedObjs.append(tempCopy)
            rs.StatusBarProgressMeterUpdate(i)
        
        #Move all copies to a different layer
        for i, obj in enumerate(copiedObjs):
            layerFullName = rs.ObjectLayer(obj)
            shortName = layerFullName.replace('::', seperator)
            layerName = baseName + seperator + shortName
            if rs.IsLayer(layerName):
                rs.ObjectLayer(obj, layerName)
            else:
                matIndex = rs.LayerMaterialIndex(rs.ObjectLayer(obj))
                newLayer = rs.AddLayer(layerName, rs.LayerColor(rs.ObjectLayer(obj)))
                rs.LayerMaterialIndex(newLayer, matIndex)
                tempLayers.append(newLayer)
                rs.ObjectLayer(obj, newLayer)
        rs.StatusBarProgressMeterHide()
        
        try:
            rs.SelectObjects(copiedObjs)
            rs.Command('-_Export ' + '"' + fileName + '"' + ' s SketchUp2015 Enter ', False)
            
            #CLEANUP
            rs.UnselectAllObjects() 
            try:
                rs.DeleteObjects(copiedObjs)
            except:
                rs.DeleteObject(copiedObjs)
            for layer in tempLayers:
                rs.DeleteLayer(layer)
        except:
            print "export failed"
        result = True
    except:
        result = False
    utils.SaveFunctionData('IO-Export to Render[SKP]', [fileName, baseName, os.path.getsize(fileName),len(objs), result])
    return result

################################################################################
#Capture Display modes
def exportImage(path, name, width, height):
    try:
        shortName = os.path.splitext(path)[0]
        fullName = shortName + '_' + name + '.png'
        comm=' -_ViewCaptureToFile '  + ' _Width=' + str(width) + ' _Height=' + str(height) + ' _Scale=1 _DrawGrid=_No _DrawWorldAxes=_No _DrawCPlaneAxes=_No _TransparentBackground=_Yes ' + '"' + fullName + '"'+ ' _Enter'
        rs.Command(comm,False)
    except:
        pass

def CaptureDisplayModesToFile():
    try:
        displayModeNames = []
        displayModeBool = []
        displayModesChecked = []
        
        for each in Rhino.Display.DisplayModeDescription.GetDisplayModes():
            displayModeNames.append(each.EnglishName)
            if each.EnglishName[:4] == 'PCPA':
                displayModeBool.append(True)
            else:
                displayModeBool.append(False)
        
        results = rs.CheckListBox(zip(displayModeNames, displayModeBool), 'Select Display Modes', 'Capture Display Modes To File')
        if results is None: return
        for each in results:
            if each[1]:
                displayModesChecked.append(each[0])
        
        date = utils.GetDatePrefix()
        if date is None: date = 'DATE'
        activeView = sc.doc.Views.ActiveView.ActiveViewport.Name
        if activeView is None: activeView = 'VIEW'
        path = rs.SaveFileName('Export All Display Modes', "PNG (*.png)|*.png||", filename = date+'_'+activeView)
        if path is None: return
        
        if 'catpureDisplays-width' in sc.sticky:
            widthDefault = sc.sticky['catpureDisplays-width']
        else:
            widthDefault = 5100
        
        if 'catpureDisplays-height' in sc.sticky:
            heightDefault = sc.sticky['catpureDisplays-height']
        else:
            heightDefault = 3300
        
        width = rs.GetInteger('Image Width', number = widthDefault, minimum = 600, maximum = 20000)
        height = rs.GetInteger('Image Height', number = heightDefault, minimum = 600, maximum = 20000)
        
        sc.sticky['catpureDisplays-width'] = width
        sc.sticky['catpureDisplays-height'] = height
        
        
        for name in displayModesChecked:
            try:
                rs.Command('-_SetDisplayMode m ' +  name  + ' Enter', False)
                exportImage(path, name, width, height)
            except:
                pass
        return True
    except:
        return False


if __name__ == "__main__":
    func = rs.GetInteger("Function to run", number = 0)
    if func == 0:
        rc = importDWG()
        if rc: utils.SaveToAnalytics('IO-Import DWG')
    elif func == 1:
        rc = exportToRenderDWG()
        if rc: utils.SaveToAnalytics('IO-Export To Render DWG')
    elif func == 2:
        rc = exportToRenderSKP()
        if rc: utils.SaveToAnalytics('IO-Export To Render SKP')
    elif func == 3:
        rc = CaptureDisplayModesToFile()
        if rc: utils.SaveToAnalytics('IO-Capture Display Modes')