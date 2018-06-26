import rhinoscriptsyntax as rs
import scriptcontext as sc
import os.path

def ExportEachLayerAsSat(objs):
    try:
        path = rs.BrowseForFolder()
        if path is None: return
        
        newFolderName = rs.StringBox(default_value='180625_OPTION_01')
        newFolder = os.path.join(path,newFolderName)
        
        if not os.path.exists(newFolder):
            os.mkdir(newFolder)
        
        allLayers = []
        for obj in objs:
            layer = rs.ObjectLayer(obj)
            if layer not in allLayers:
                allLayers.append(layer)
        
        for eachLayer in allLayers:
            try:
                filepath = os.path.join(newFolder,newFolderName+ '_' + eachLayer + '.sat')
                rhobjs = sc.doc.Objects.FindByLayer(eachLayer)
                rs.SelectObjects(rhobjs)
                print ""
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        pass

objs = rs.VisibleObjects()
ExportEachLayerAsSat(objs)