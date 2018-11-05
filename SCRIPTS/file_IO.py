import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import random
import System.Drawing
import os.path

import layers
import blocks
import config
import utils
import standards

__author__ = 'Tim Williams'
__version__ = "2.1.0"

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

def importCAD(filePath, scaleDWG = False):
    explodeBlockBoo = True

    #setup the layers
    importLayerNumber = 6000
    importLayerObj = layers.AddLayerByNumber(importLayerNumber, False)
    importLayerName = layers.GetLayerNameByNumber(importLayerNumber)

    #Shorten cad file name
    fileNameExt = os.path.basename(filePath)
    fileName = os.path.splitext(fileNameExt)[0]
    
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
    
    rs.Command('_-Import "' + filePath + '" _IgnoreThickness=Yes _ModelUnits=Inches _Enter', False)

    #get new layers added
    endLayersNames = rs.LayerNames()
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

    #Collapse layers
    try:
        rootLay = sc.doc.Layers.FindId(rs.coerceguid(rs.LayerId(elementLayerName)))
        rootLay.IsExpanded = False
    except:
        pass
    print "Import Successful"
    return finalAllObjects

def importCAD_Button():
    try:
        #Import CAD
        filePath = rs.OpenFileName("Select CAD to Import", "Autocad (*.dwg)|*.dwg||")
        if filePath is None: return None
    
        rs.EnableRedraw(False)
        group = rs.AddGroup('Import CAD Group')
        allImportedObjects = importCAD(filePath)
        rs.AddObjectsToGroup(allImportedObjects, group)
        rs.EnableRedraw(True)
        result = True
    except:
        print "Import Failed"
        result = False
    try:
        utils.SaveFunctionData('IO-Import CAD',[result])
    except:
        print "Failed to save function data"
    return result

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
        if utils.IsSavedInProjectFolder():
            origPath = rs.DocumentPath()
            path = os.path.normpath(origPath)
            pathParts = path.split(os.sep)
            projectFolder = os.path.join(pathParts[0],'\\' ,pathParts[1])
            referenceFolder = os.path.join(projectFolder, r'03 DRAWINGS\02 RENDERING\0_copy 3d  folder structure\Reference')
            if os.path.isdir(referenceFolder):
                print "Reference folder exists"
                defaultFolder = referenceFolder
            else: 
                print "Reference folder not found"
                defaultFolder = rs.DocumentPath()
        else:
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
    try:
        utils.SaveFunctionData('IO-Export to Render[SKP]', [fileName, baseName, os.path.getsize(fileName),len(objs), result])
    except:
        print "Failed to save function data"
    return result

################################################################################
#Capture Display modes
def exportImage(path, name, width, height):
    try:
        shortName = os.path.splitext(path)[0]
        fullName = shortName + '_' + name + '.png'
        comm='-_ViewCaptureToFile u p _Width=' + str(width) + ' _Height=' + str(height) + ' _Scale=1 _LockAspectRatio=No _DrawGrid=No _DrawWorldAxes=No _TransparentBackground=_Yes "' + fullName + '" _Enter'
        rs.Command(comm,False)
    except:
        pass

def CaptureDisplayModesToFile():
    try:
        displayModeNames = []
        displayModeBool = []
        displayModesChecked = []
        
        ########
        #Get current display mode
        originalDisplayMode = rc.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.DisplayMode.LocalName
        
        ########
        #Get default display mode selection
        if 'CaptureDisplayModes-DisplayModes' in sc.sticky:
            dict = sc.sticky['CaptureDisplayModes-DisplayModes']
            for each in rc.Display.DisplayModeDescription.GetDisplayModes():
                displayModeNames.append(each.EnglishName)
                if each.EnglishName in dict:
                    displayModeBool.append(dict[each.EnglishName])
                else:
                    displayModeBool.append(False)
        else:
            for each in rc.Display.DisplayModeDescription.GetDisplayModes():
                displayModeNames.append(each.EnglishName)
                displayModeBool.append(False)
        
        results = rs.CheckListBox(zip(displayModeNames, displayModeBool), 'Select Display Modes', 'Capture Display Modes To File')
        if results is None: return
        
        ########
        #Save display modes to sticky
        resultDict = {}
        for each in results:
            resultDict[each[0]] = each[1]
        sc.sticky['CaptureDisplayModes-DisplayModes'] = resultDict
        
        for each in results:
            if each[1]:
                displayModesChecked.append(each[0])
        
        ########
        #Get default filename
        date = utils.GetDatePrefix()
        activeView = sc.doc.Views.ActiveView.ActiveViewport.Name
        if activeView is None: activeView = 'VIEW'
        path = rs.SaveFileName('Export All Display Modes', "PNG (*.png)|*.png||", filename = date+'_'+activeView)
        if path is None: return
        
        ########
        #Get sizes from sticky
        if 'catpureDisplays-width' in sc.sticky:
            widthDefault = sc.sticky['catpureDisplays-width']
        else:
            widthDefault = 5100

        if 'catpureDisplays-height' in sc.sticky:
            heightDefault = sc.sticky['catpureDisplays-height']
        else:
            heightDefault = 3300

        width = rs.GetInteger('Image Width', number = widthDefault, minimum = 200, maximum = 20000)
        height = rs.GetInteger('Image Height', number = heightDefault, minimum = 200, maximum = 20000)

        ########
        #Save sizes to sticky
        sc.sticky['catpureDisplays-width'] = width
        sc.sticky['catpureDisplays-height'] = height

        #######################################################################
        #Export the images
        count = 0
        for name in displayModesChecked:
            try:
                rs.ViewDisplayMode(mode = name)
                exportImage(path, name, width, height)
                count += 1
            except:
                pass
        print "{} Images saved to {}".format(count , os.path.abspath(os.path.join(path, os.pardir)))
        result = True
    except:
        result = False
    ########
    #Restore original display mode
    if originalDisplayMode is not None:
        rs.ViewDisplayMode(mode = originalDisplayMode)
    
    ########
    #Save analytics
    try:
        utils.SaveFunctionData('IO-Capture Display Modes', [__version__, str(displayModesChecked), width, height, result])
    except: print "Failed to save function data"
    return result

################################################################################
#Safe Capture
def SafeCapture(filePath, width, height, transparent = True):
    """
    Saves the active viewport to png
    """
    try:
        #Get the view
        view = sc.doc.Views.ActiveView
        
        #Get sizes
        size = System.Drawing.Size(width,height)
        origSize = view.ActiveViewport.Size
        
        #Change viewport size
        view.Size = size
        
        #Create the capture
        mainCapture = rc.Display.ViewCapture()
        mainCapture.DrawAxes = False
        mainCapture.DrawGridAxes = False
        mainCapture.TransparentBackground = transparent
        mainCapture.Width = width
        mainCapture.Height = height
        capture = mainCapture.CaptureToBitmap(view)
        capture.Save(filePath)
        
        #Restore viewport size
        view.Size = origSize
        return True
    except:
        return None

def SafeCaptureButton():
    #Save file name
    path = rs.SaveFileName('Save view location', "PNG (*.png; *.png)|")
    if path is None: return
    
    splitPath = path.Split(".")
    if len(splitPath)<2:
        path += ".png"
    
    #Check if in stick
    if 'safeCapture-width' in sc.sticky:
        defaultWidth = sc.sticky['safeCapture-width']
    else:
        defaultWidth = 5100
    if 'safeCapture-height' in sc.sticky:
        defaultHeight = sc.sticky['safeCapture-height']
    else:
        defaultHeight = 3300
    
    #Get output width
    width =  rs.GetInteger('Width', defaultWidth, 200, 10000 )
    if width is None: return
    sc.sticky['safeCapture-width'] = width
    
    #Get output height
    height = rs.GetInteger('Height', defaultHeight, 200, 10000 )
    if height is None: return
    sc.sticky['safeCapture-height'] = height
    
    result = SafeCapture(path, width, height)
    if result:
        print "Image saved as {}".format(path)
        return True
    else:
        return None

################################################################################
#Batch view export
def BatchCapture():
    try:
        namedViews = rs.NamedViews()
        if len(namedViews) < 1: 
            print "There are no Named Views in this file."
            return None
        
        #Prepare checklis
        items = []
        for view in namedViews:
            items.append([view, False])
        
        #Checklist
        returnedVals = rs.CheckListBox(items, "Select Views to Export", "Batch Capture")
        if returnedVals is None: return
        
        chosenViews = []
        for val in returnedVals:
            if val[1]:
                chosenViews.append(val[0])
        if len(chosenViews) < 1: return
        
        date = utils.GetDatePrefix()
        path = rs.SaveFileName('Batch Capture', "PNG (*.png)|*.png||", filename = date+'_FILENAME')
        if path is None: return
        
        #Check if in stick
        if 'batchCapture-width' in sc.sticky:
            defaultWidth = sc.sticky['batchCapture-width']
        else:
            defaultWidth = 5100
        if 'batchCapture-height' in sc.sticky:
            defaultHeight = sc.sticky['batchCapture-height']
        else:
            defaultHeight = 3300
        
        #Get output width
        width =  rs.GetInteger('Width', defaultWidth, 200, 10000 )
        if width is None: return
        sc.sticky['batchCapture-width'] = width
        
        #Get output height
        height = rs.GetInteger('Height', defaultHeight, 200, 10000 )
        if height is None: return
        sc.sticky['batchCapture-height'] = height
        
        rs.AddNamedView("temp")
        
        baseName = os.path.splitext(path)[0]
        for eachView in chosenViews:
            rs.RestoreNamedView(eachView)
            filePath = baseName + "_" + eachView + ".png"
            
            SafeCapture(filePath, width, height)
        
        #return to original view
        rs.RestoreNamedView("temp")
        rs.DeleteNamedView("temp")
        
        
        result = True
    except:
        result = False
    utils.SaveFunctionData('IO-BatchCapture', [__version__] + chosenViews)
    return result

if __name__ == "__main__":
    func = rs.GetInteger("Function to run", number = 0)
    if func == 0:
        result = importCAD_Button()
        if result: utils.SaveToAnalytics('IO-Import CAD')
    elif func == 1:
        result = exportToRenderDWG()
        if result: utils.SaveToAnalytics('IO-Export To Render DWG')
    elif func == 2:
        result = exportToRenderSKP()
        if result: utils.SaveToAnalytics('IO-Export To Render SKP')
    elif func == 3:
        result = CaptureDisplayModesToFile()
        if result: utils.SaveToAnalytics('IO-Capture Display Modes')
    elif func == 4:
        result = SafeCaptureButton()
        if result: utils.SaveToAnalytics('IO-Safe Capture')
    elif func == 5:
        result = BatchCapture()
        if result: utils.SaveToAnalytics('IO-Batch Capture')
