import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


def FindObjByKey(key):
    objTable = sc.doc.Objects
    enum = Rhino.DocObjects.ObjectType.AnyObject
    x = list(objTable.FindByUserString(key, '*', True, True, True, enum))
    guidList = []
    
    
    for each in x:
        guidList.append(each.Id)
    
    return guidList

key = 'Test'
guids = FindObjByKey(key)
for each in guids:
    
    print rs.GetUserText(each, key)
rs.SelectObjects(guids)