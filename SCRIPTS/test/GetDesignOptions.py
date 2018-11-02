import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

def GetDesignOptionBlockNames():
    #layer = rs.GetLayer()
    objSettings = rc.DocObjects.ObjectEnumeratorSettings()
    objSettings.IncludeLights = False
    objSettings.IncludeGrips = False
    #objSettings.NormalObjects = True
    #objSettings.LockedObjects = True
    #objSettings.HiddenObjects = True
    objSettings.ReferenceObjects = False
    #objSettings.SelectedObjectsFilter = True
    rhobjs = sc.doc.Objects.FindByUserString('Design Option History', '*', False,)
    for rhobj in rhobjs:
        layerName = sc.doc.Layers.FindIndex(rhobj.Attributes.LayerIndex)
        print 'Found option "{}" on layer "{}"'.format(rhobj.InstanceDefinition.Name, layerName)

GetDesignOptionBlockNames()