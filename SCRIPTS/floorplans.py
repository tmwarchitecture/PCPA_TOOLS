import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import database_tools as dt

"""
To-do:

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
        finalHeights.append(float(eachLevel[4]))
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
        try:
            rs.JoinCurves(xCurves)
        except:
            pass
        for curve in xCurves:
            finalCurve = sc.doc.Objects.AddCurve(curve)
            rs.SetUserText(finalCurve, 'PCPA_floorplan', 'intersect')
            intersectionCrvs.append(finalCurve)
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
    print "!"
    for obj in objs:
        if rs.IsBrep(obj):
            #dupObj = rs.CopyObject(obj)
            if rs.IsPolysurfaceClosed(obj):
                newObj = rs.BooleanDifference(obj, negShapeGeo, False)
                if newObj is None:
                    newSplitObjs.append(obj)
                elif len(newObj) < 1:
                    newSplitObjs.append(obj)
                else:
                    for each in newObj:
                        newSplitObjs.append(each)
                    rs.DeleteObject(obj)
            else:
                print "!"
                newObjs = rs.SplitBrep(obj, negShapeGeo)
                print "!"
                if newObjs is None:
                    newSplitObjs.append(obj)
                    rs.DeleteObject(obj)
                else:
                    #Find the geo below the plane
                    partitionGeos = PartitionGeometryCenter(newObjs, plane.OriginZ)
                    if dir == 1:
                        newSplitObjs += partitionGeos[0]
                        rs.DeleteObjects(partitionGeos[2])
                    else:
                        newSplitObjs += partitionGeos[2]
                        rs.DeleteObjects(partitionGeos[0])
                    #rs.DeleteObject(obj)
    
    
    rs.DeleteObject(negShapeGeo)
    return newSplitObjs

def PartitionGeometry(objs, elevation, viewDepth):
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
        if highestCoord < viewDepth:
            objsBelow.append(obj)
            continue
        objsInter.append(obj)
    return [objsBelow, objsInter, objsAbove]

def PartitionGeometryCenter(objs, elevation):
    objsBelow = []
    objsInter = []
    objsAbove = []
    for obj in objs:
        pts = rs.BoundingBox(obj)
        lowestCoord = pts[0][2]
        highestCoord = pts[-1][2]
        centerPtZ = (lowestCoord + highestCoord)/2
        if centerPtZ > elevation:
            objsAbove.append(obj)
            continue
        if centerPtZ < elevation:
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
    
    rs.AddNamedCPlane('c_prev')
    rs.AddNamedCPlane('c_temp')
    rs.ViewCPlane(plane = plane)
    rs.Command('-_Make2d l c p f _Enter', False)
    
    projLines = rs.SelectedObjects()
    
    rs.DeleteNamedCPlane('c_temp')
    rs.RestoreNamedCPlane('c_prev')
    rs.DeleteNamedCPlane('c_prev')
    for line in projLines:
        rs.ObjectColor(line, (200,200,200))
    return projLines

def MakePlan(elevation, viewDepthZ, geos):
    objs = rs.CopyObjects(geos)
    ############################################################################
    print "Cutting Plan"
    allCrvs = []
    
    #Make plane
    plane = Rhino.Geometry.Plane(rs.coerce3dpoint((0,0,elevation)), rs.coerce3dvector((0,0,1)))
    planeNeg = Rhino.Geometry.Plane(rs.coerce3dpoint((0,0,viewDepthZ)), rs.coerce3dvector((0,0,1)))
    
    ############################################################################
    #Partition the geometry
    
    partitionedObjs = PartitionGeometry(objs, elevation, viewDepthZ)
    
    ############################################################################
    #Intersection Curves
    
    interCrvs = IntersectGeos(partitionedObjs[1], plane)
    
    ############################################################################
    #Split Geometry
    
    #Get the bottom half of intersecting objs
    belowObjs = SplitGeometry(partitionedObjs[1], plane)
    rs.SelectObjects(belowObjs)
    
    #Get the top half of that previous geometry
    belowObjs2 = SplitGeometry(partitionedObjs[0] + belowObjs, planeNeg, -1)
    
    rs.DeleteObjects(belowObjs)
    rs.SelectObjects(belowObjs2)
    
    ############################################################################
    #Make 2D
    
    #Hide objects outside of the viewing box
    rs.HideObjects(partitionedObjs[1])
    rs.HideObjects(partitionedObjs[2])
    
    #make 2d
    allCrvs += ProjectPlan(belowObjs2, plane)
    
    #Show those hidden objects again
    rs.ShowObjects(partitionedObjs[1])
    rs.ShowObjects(partitionedObjs[2])
    
    #Delete the temporary objects
    rs.DeleteObjects(belowObjs2)
    
    print "Plan Cut"
    rs.HideObjects(allCrvs)
    return allCrvs

def main():
    rs.EnableRedraw(False)
    
    global diffRadius
    diffRadius = 9999
    viewOffset = 12
    
    #lvls = GetLevels()
    lvls = [0, 195]
    
    #geos = rs.ObjectsByLayer('test')
    geos = rs.VisibleObjects()
    
    make2Dlines = []
    for i, lvl in enumerate(lvls):
        if i == 0:
            viewDepthZ = 0
        else:
            viewDepthZ = lvls[i-1] + viewOffset
        make2Dlines += MakePlan(lvl + viewOffset, viewDepthZ, geos)
    rs.ShowObjects(make2Dlines)
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()