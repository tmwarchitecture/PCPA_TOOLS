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
        print ""
        for eachLayer in allLayers:
            try:
                
                print "1"
                #FindByLayer doesnt work with full layer names
                id = rs.LayerId(eachLayer)
                shortName = rs.LayerName(id, False)
                
                filepath = os.path.join(newFolder,newFolderName+ '_' + shortName + '.sat')
                
                rhobjs = sc.doc.Objects.FindByLayer(shortName)
                print "2"
                rs.SelectObjects(rhobjs)
                print "3"
                rs.Command('-_Export ' + '"' + filepath + '"' + ' Enter ')
                rs.UnselectAllObjects() 
            except:
                pass
    except:
        pass

objs = rs.VisibleObjects()
ExportEachLayerAsSat(objs)