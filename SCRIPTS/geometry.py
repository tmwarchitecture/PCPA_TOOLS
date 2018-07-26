import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import math
import utils

def IntersectGeo(obj, level):
    tolerance = rs.UnitAbsoluteTolerance()
    
    brep = rs.coercebrep(obj)
    intersectionCrvs = []
    if brep is None: return
    
    plane = Rhino.Geometry.Plane(rs.coerce3dpoint((0,0,level)), rs.coerce3dvector((0,0,1)))
    x = Rhino.Geometry.Intersect.Intersection.BrepPlane(brep, plane, tolerance)
    xCurves = x[1]
    if xCurves is None: return
    try:
        newCurves = Rhino.Geometry.Curve.JoinCurves(xCurves)
        #newCurves = rs.JoinCurves(xCurves)
    except:
        newCurves = xCurves
    #if len(xCurves)>1:
    #    rs.DeleteObjects(xCurves)
    #else:
    #    rs.DeleteObject(xCurves)
    finalCurves = []
    for curve in newCurves:
        finalCurve = sc.doc.Objects.AddCurve(curve)
        rs.MatchObjectAttributes(finalCurve, obj)
        finalCurves.append(finalCurve)
    sc.doc.Views.Redraw()
    return finalCurves

def IntersectGeoAtPt():
    try:
        objs = rs.GetObjects("Select objects to contour", 1073741848, False, True)
        if objs is None: return
        pt = rs.GetPoint("Select point to contour at")
        if pt is None: return
        ptZ = pt[2]
        geos = []
        for obj in objs:
            try:
                geos += IntersectGeo(obj, ptZ)
            except:
                pass
        rs.SelectObjects(geos)
        return True
    except:
        return False

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
                    newVec = Rhino.Geometry.Vector3d.Multiply(tanSt,dist)
                    elbowPt = Rhino.Geometry.Point3d.Add(stPt, newVec)
                    plinePts = [stPt, elbowPt, endPt]
                    pline = Rhino.Geometry.Polyline(plinePts)
                    newSegments.append(sc.doc.Objects.AddPolyline(pline))
            elif rs.IsLine(segment):
                stPt = segment.PointAtStart
                endPt = segment.PointAtEnd
                lineSeg = Rhino.Geometry.Line(stPt, endPt)
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
    #Will remove entire pline when angle > 180 degrees
    objs = rs.GetObjects("Select curves to unfillet", rs.filter.curve, True, True)
    if objs is None: return
    
    bool = False
    for obj in objs:
        result = unfilletObj(obj)
        if result is not None: bool = True
    return bool

if __name__ == "__main__":
    func = rs.GetInteger("func num")
    if func == 0:
        result = IntersectGeoAtPt()
        if result:
            utils.SaveToAnalytics('geometry-Contour At Pt')
    if func == 1:
        result = unfillet()
        if result:
            utils.SaveToAnalytics('geometry-Unfillet')