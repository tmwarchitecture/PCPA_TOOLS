import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

def GetAllBlockObjectsInPosition(obj):
    """Recursively get all objects from a block (and blocks in blocks)
    inputs:
        obj (block instance)
    returns:
        objs (list guids): Geometry is a copy of the instance geometry
    """
    blockObjs = rs.BlockObjects(rs.BlockInstanceName(obj))
    xform = rs.BlockInstanceXform(obj)
    objList = []
    for eachblockObj in blockObjs:
        if rs.IsBlockInstance(eachblockObj):
            thisBlockObjects = GetAllBlockObjectsInPosition(eachblockObj)
            for eachObject in thisBlockObjects:
                transformedObj = rs.TransformObject(eachObject, xform, False)
                objList.append(transformedObj)
        else:
            transformedObj = rs.TransformObject(eachblockObj, xform, True)
            objList.append(transformedObj)
    return objList


def main():
    objs = rs.GetObjects()
    rs.EnableRedraw(False)
    for obj in objs:
        final = GetAllBlockObjectsInPosition(obj)
        for each in final:
            rs.ObjectColor(each, (255,0,0))
    rs.EnableRedraw(True)

main()