import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import database_tools as dt

__author__ = 'Tim Williams'
__version__ = "2.1.0"

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

    visibleGeometry = []

    for obj in objs:
        if rs.IsBrep(obj):
            if rs.IsPolysurfaceClosed(obj):
                resultObjs = rs.BooleanDifference(obj, negShapeGeo, False)
                if resultObjs is None:
                    visibleGeometry.append(obj)
                elif len(resultObjs) < 1:
                    visibleGeometry.append(obj)
                else:
                    for each in resultObjs:
                        visibleGeometry.append(each)
            else:
                resultObjs = rs.SplitBrep(obj, negShapeGeo)
                if resultObjs is None:
                    visibleGeometry.append(obj)
                elif len(resultObjs) < 1:
                    visibleGeometry.append(obj)
                else:
                    for each in resultObjs:
                        if IsAbovePlane(each, plane.OriginZ):
                            if dir == -1:
                                visibleGeometry.append(each)
                            else:
                                rs.DeleteObject(each)
                        else:
                            if dir == 1:
                                visibleGeometry.append(each)
                            else:
                                rs.DeleteObject(each)

    rs.DeleteObject(negShapeGeo)
    return visibleGeometry

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

def IsAbovePlane(obj, elevation):
    pts = rs.BoundingBox(obj)
    lowestCoord = pts[0][2]
    highestCoord = pts[-1][2]
    centerPtZ = (lowestCoord + highestCoord)/2
    if centerPtZ > elevation:
        return True
    else:
        return False

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
    rs.HideObjects(geos)

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

    #interCrvs = IntersectGeos(partitionedObjs[1], plane)

    ############################################################################
    #Split Geometry
    #Get the bottom half of intersecting objs
    belowObjs = SplitGeometry(partitionedObjs[1], plane)
    print "A"

    #Get the top half of that previous geometry
    visibleObjs = SplitGeometry(partitionedObjs[0] + belowObjs, planeNeg, -1)

    rs.SelectObjects(visibleObjs)
    objs2del = rs.InvertSelectedObjects()
    rs.DeleteObjects(objs2del)
    print "A"
    ############################################################################
    #Make 2D
    allCrvs += ProjectPlan(visibleObjs, plane)

    rs.DeleteObjects(visibleObjs)

    print "Plan Cut"
    rs.ShowObjects(geos)
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
        make2Dlines.append(MakePlan(lvl + viewOffset, viewDepthZ, geos))
    #make2Dlines = MakePlan(12, 0+0, geos)
    #rs.ShowObjects(make2Dlines)
    rs.EnableRedraw(True)

if __name__ == "__main__" and utils.IsAuthorized():
    main()
