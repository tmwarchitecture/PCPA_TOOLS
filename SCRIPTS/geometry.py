import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math
import utils

__author__ = 'Tim Williams'
__version__ = "2.1.0"

################################################################################
#INTERSECT AT POINT
def IntersectBrepPlane(obj, plane):
    tolerance = rs.UnitAbsoluteTolerance()
    #BREP
    brep = rs.coercebrep(obj)
    intersectionCrvs = []
    if brep is None: return None

    x = rc.Geometry.Intersect.Intersection.BrepPlane(brep, plane, tolerance)
    if x is None: return

    xCurves = x[1]
    if xCurves is None: return None

    try:
        newCurves = rc.Geometry.Curve.JoinCurves(xCurves)
    except:
        newCurves = xCurves

    finalCurves = []

    for curve in newCurves:
        finalCurve = sc.doc.Objects.AddCurve(curve)
        rs.MatchObjectAttributes(finalCurve, obj)
        finalCurves.append(finalCurve)

    return finalCurves

def IntersectGeo(obj, level):
    tolerance = rs.UnitAbsoluteTolerance()
    plane = rc.Geometry.Plane(rs.coerce3dpoint((0,0,level)), rs.coerce3dvector((0,0,1)))
    finalCurves = []
    #BLOCKS
    if rs.IsBlockInstance(obj):
        matrix = rs.BlockInstanceXform(obj)
        blockObjs = rs.BlockObjects(rs.BlockInstanceName(obj))
        for eachBlockObj in blockObjs:
            newCopy = rs.CopyObject(eachBlockObj)
            xformedObj = rs.TransformObject(newCopy, matrix)

            #EXTRUSIONS
            if isinstance(xformedObj, rc.Geometry.Extrusion):
                temp = sc.doc.Objects.AddBrep(xformedObj.ToBrep(False))
                xformedObj = rs.coercebrep(temp)
                rs.DeleteObject(temp)

            #BREPS IN BLOCK
            result = IntersectBrepPlane(xformedObj, plane)
            if result is None: continue
            for each in result:
                if each is not None:
                    finalCurves.append(each)
            rs.DeleteObject(xformedObj)
    #BREPS
    elif rs.IsBrep(obj):
        result = IntersectBrepPlane(obj, plane)
        if result is None: return None
        for each in result:
            if each is not None:
                finalCurves.append(each)
    return finalCurves

def IntersectGeoAtPt():
    try:
        objs = rs.GetObjects("Select objects to contour",1073745980, preselect = True)
        if objs is None: return

        pt = rs.GetPoint("Select point to contour at")
        if pt is None: return

        rs.EnableRedraw(False)
        geos = []
        for obj in objs:
            if rs.IsBlockInstance(obj):
                blocksObjects = utils.GetAllBlockObjectsInPosition(obj)
                for eachBlocksObject in blocksObjects:
                    result = IntersectGeo(eachBlocksObject, pt.Z)
                    if result is None: continue
                    for each in result:
                        if each is not None:
                            geos.append(each)
                    rs.DeleteObject(eachBlocksObject)
            else:
                result = IntersectGeo(obj, pt.Z)
                if result is None: continue
                for each in result:
                    if each is not None:
                        geos.append(each)
        rs.EnableRedraw(True)

        rs.SelectObjects(geos)
        result = True
    except:
        result = False
    utils.SaveFunctionData('Geometry-Contour At Pt', [__version__, len(objs), pt.Z, result])
    return result

################################################################################
#UNFILLET
def unfilletObj(obj):
    try:
        rhobj = rs.coercecurve(obj)

        segments = rhobj.DuplicateSegments()
        newSegments = []
        for i, segment, in enumerate(segments):
            if rs.IsArc(segment):
                stPt = segment.PointAtStart
                endPt = segment.PointAtEnd
                tanSt = segment.TangentAtStart
                angle = segment.AngleRadians/2
                if segment.AngleRadians >= math.pi:
                    newSegments.append(sc.doc.Objects.AddArc(segment.Arc))
                else:
                    dist = (math.tan(angle)) * segment.Radius
                    newVec = rc.Geometry.Vector3d.Multiply(tanSt,dist)
                    elbowPt = rc.Geometry.Point3d.Add(stPt, newVec)
                    plinePts = [stPt, elbowPt, endPt]
                    pline = rc.Geometry.Polyline(plinePts)
                    newSegments.append(sc.doc.Objects.AddPolyline(pline))
            elif rs.IsLine(segment):
                stPt = segment.PointAtStart
                endPt = segment.PointAtEnd
                lineSeg = rc.Geometry.Line(stPt, endPt)
                newSegments.append(sc.doc.Objects.AddLine(lineSeg))

        joinedSegs = rs.JoinCurves(newSegments, True)
        rs.SimplifyCurve(joinedSegs)
        rs.MatchObjectAttributes(joinedSegs, obj)
        rs.DeleteObject(obj)
        sc.doc.Views.Redraw()
        return joinedSegs
    except:
        print "Unfillet Failed"
        return None

def unfillet():
    try:
        #Will remove entire pline when angle > 180 degrees
        objs = rs.GetObjects("Select curves to unfillet", rs.filter.curve, True, True)
        if objs is None: return
        
        successList = []
        for obj in objs:
            unfilletResult = unfilletObj(obj)
            if unfilletResult is None: 
                successList.append(False)
            else: successList.append(True)
        result = True
    except:
        result = False
    utils.SaveFunctionData('Geometry-Unfillet', [__version__, len(objs), str(successList), result])
    return result

if __name__ == "__main__":
    func = rs.GetInteger("func num")
    if func == 0:
        result = IntersectGeoAtPt()
        if result:
            utils.SaveToAnalytics('Geometry-Contour At Pt')
    if func == 1:
        result = unfillet()
        if result:
            utils.SaveToAnalytics('Geometry-Unfillet')
