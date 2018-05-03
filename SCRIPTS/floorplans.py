import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import database_tools as dt

"""
To-do:
Make sure projected plans are not in the make2d

"""

def GetLevels():
    try:
        path = rs.GetDocumentData('PCPA', 'Project_Database')
    except:
        print "No level data set"
        path = ''
    levelData = dt.GetProjectLevelData(path, 0)
    finalHeights = []
    for eachLevel in levelData:
        finalHeights.append(float(eachLevel[4])*12)
    return finalHeights

def IntersectGeos(objs, plane):
    tolerance = rs.UnitAbsoluteTolerance()
    finalGeo = []
    for obj in objs:
        intersectionCrvs = []
        brep = rs.coercebrep(obj)
        if brep is None: continue
        x = Rhino.Geometry.Intersect.Intersection.BrepPlane(brep, plane, tolerance)
        xCurves = x[1]
        if xCurves is None: continue
        for curve in xCurves:
            intersectionCrvs.append(sc.doc.Objects.AddCurve(curve))
            finalGeo.append(intersectionCrvs)
        rs.MatchObjectAttributes(intersectionCrvs, obj)
    return finalGeo

def SplitGeometry(objs, plane, dir = 1):
    global diffRadius
    circle = Rhino.Geometry.Circle(plane, diffRadius)
    negShape = Rhino.Geometry.Cylinder(circle, diffRadius*dir)
    negShapeBrep = negShape.ToBrep(True, True)
    negShapeGeo = sc.doc.Objects.AddBrep(negShapeBrep)
    newSplitObjs = []
    for obj in objs:
        if rs.IsBrep(obj):
            if rs.IsPolysurfaceClosed(obj):
                dupObj = rs.CopyObject(obj)
                newObj = rs.BooleanDifference(dupObj, negShapeGeo, False)
                if newObj is not None:
                    for each in newObj:
                        newSplitObjs.append(each)
                rs.DeleteObject(dupObj)
    rs.DeleteObject(negShapeGeo)
    return newSplitObjs

def PartitionGeometry(objs, elevation):
    objsBelow = []
    objsInter = []
    objsAbove = []
    for obj in objs:
        pts = rs.BoundingBox(obj)
        lowestCoord = pts[0][2]
        highestCoord = pts[-1][2]
        
        if lowestCoord > elevation:
            objsAbove.append(obj)
            continue
        if highestCoord < elevation:
            objsBelow.append(obj)
            continue
        objsInter.append(obj)
    return [objsBelow, objsInter, objsAbove]

def ProjectPlan(objs, plane):
    print "Projecting Plan"
    try:
        rs.SelectObjects(objs)
    except:
        rs.SelectObject(objs)
    
    rs.AddNamedCPlane('c_temp')
    rs.ViewCPlane(plane = plane)
    rs.Command('-_Make2d l c p f _Enter', False)
    
    projLines = rs.SelectedObjects()
    
    rs.DeleteNamedCPlane('c_temp')
    for line in projLines:
        rs.ObjectColor(line, (200,200,200))
    return projLines

def MakePlan(elevation, geos):
    print "Cutting Plan"
    plane = Rhino.Geometry.Plane(rs.coerce3dpoint((0,0,elevation)), rs.coerce3dvector((0,0,1)))
    
    global viewDepth
    viewDepthElev = elevation - viewDepth
    planeNeg = Rhino.Geometry.Plane(rs.coerce3dpoint((0,0,viewDepthElev)), rs.coerce3dvector((0,0,1)))
    
    partitionedObjs = PartitionGeometry(geos, elevation)
    
    #IntersectGeos(partitionedObjs[1], plane)
    belowObjs = SplitGeometry(partitionedObjs[1], plane)
    
    belowObjs2 = SplitGeometry(partitionedObjs[0] + belowObjs, planeNeg, -1)
    
    rs.DeleteObjects(belowObjs)
    
    rs.HideObjects(partitionedObjs[1])
    rs.HideObjects(partitionedObjs[2])
    
    ProjectPlan(belowObjs2, plane)
    
    rs.ShowObjects(partitionedObjs[1])
    rs.ShowObjects(partitionedObjs[2])
    rs.DeleteObjects(belowObjs)
    rs.DeleteObjects(belowObjs2)
    print "Plan Cut"

def main():
    rs.EnableRedraw(False)
    
    global diffRadius
    diffRadius = 999
    global viewDepth
    viewDepth = 3*12
    global viewOffset
    viewOffset = 12
    
    lvls = GetLevels()
    geos = rs.ObjectsByLayer('test')
    for i, lvl in enumerate(lvls):
        MakePlan(lvl + viewOffset, geos)
    #MakePlan(70, geos)
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()