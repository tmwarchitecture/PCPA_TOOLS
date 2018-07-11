import rhinoscriptsyntax as rs
import scriptcontext as sc
import os.path

def ExportEachLayerAsSat(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.sat')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsSat failed'

def ExportEachLayerAs3DS(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.3ds')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsSat failed'

def ExportEachLayerAsDAE(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.dae')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsSat failed'

def ExportEachLayerAsIGES(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.igs')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' "3DS MAX 5.0" Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsSat failed'

def ExportEachLayerAsOBJ(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.obj')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsSat failed'

def ExportAsSKP(objs, newFolder, newFolderName):
    tempLayers = []
    
    copiedObjs = []
    
    rs.StatusBarProgressMeterShow('Exporting to SKP', 0, len(objs))
    
    for i, obj in enumerate(objs):
        tempCopy = rs.CopyObject(obj)
        rs.ObjectLayer(tempCopy, rs.ObjectLayer(obj))
        copiedObjs.append(tempCopy)
        rs.StatusBarProgressMeterUpdate(i)
    
    for obj in copiedObjs:
        shortName = rs.LayerName(rs.ObjectLayer(obj), False)
        layerName = newFolderName + '_' + shortName
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
        filepath = os.path.join(newFolder,newFolderName + '.skp')
        rs.SelectObjects(copiedObjs)
        rs.Command('-_Export ' + '"' + filepath + '"' + ' s SketchUp2015 Enter ', False)
        
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

def ExportEachLayerAsDXF(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.dxf')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter Enter')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsDXF failed'

def ExportEachLayerAsDWG(objs, newFolder, newFolderName):
    try:
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.dwg')
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                rs.SelectObjects(rhobjs)
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter Enter')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        print 'ExportEachLayerAsDXF failed'


def main():
    path = rs.BrowseForFolder()
    if path is None: return
    
    newFolderName = rs.StringBox(default_value='180710_TEST_01')
    newFolder = os.path.join(path,newFolderName)
    
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)    
    
    objs = rs.VisibleObjects()
    
    #ExportEachLayerAsSat(objs, newFolder, newFolderName)
    #ExportEachLayerAs3DS(objs, newFolder, newFolderName)
    #ExportEachLayerAsDAE(objs, newFolder, newFolderName)
    #ExportEachLayerAsIGES(objs, newFolder, newFolderName)
    #ExportEachLayerAsOBJ(objs, newFolder, newFolderName)
    ExportAsSKP(objs, newFolder, newFolderName)
    #ExportEachLayerAsDXF(objs, newFolder, newFolderName)
    #ExportEachLayerAsDWG(objs, newFolder, newFolderName)

if __name__ == "__main__":
    main()
