import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math
import utils

__author__ = 'Tim Williams'
__version__ = "2.2.0"

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
        utils.SafeMatchObjectAttributes(finalCurve, obj)
        finalCurves.append(finalCurve)

    return finalCurves

def IntersectMeshPlane(obj, plane):
    tolerance = rs.UnitAbsoluteTolerance()
    #BREP
    mesh = rs.coercemesh(obj)
    intersectionCrvs = []
    if mesh is None: return None
    
    x = rc.Geometry.Intersect.Intersection.MeshPlane(mesh, plane)
    if x is None: return
    
    #Match attributes
    finalCurves = []
    for curve in x:
        finalCurve = sc.doc.Objects.AddPolyline(curve)
        utils.SafeMatchObjectAttributes(finalCurve, obj)
        #rs.MatchObjectAttributes(finalCurve, obj) BROKEN
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
            
            #MESHES IN BLOCK <---This code might not be necessary
            result = IntersectMeshPlane(xformedObj, plane)
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
    
    #MESHES
    elif rs.IsMesh(obj):
        result = IntersectMeshPlane(obj, plane)
        if result is None: return None
        for each in result:
            if each is not None:
                finalCurves.append(each)
    return finalCurves

def IntersectGeoAtPt():
    try:
        objs = rs.GetObjects("Select objects to contour",1073745980, preselect = True)
        if objs is None: return

        geos = []
        while True:
            pt = rs.GetPoint("Select point to contour at")
            if pt is None: break

            rs.EnableRedraw(False)

            for obj in objs:
                if rs.IsBlockInstance(obj):
                    blocksObjects = utils.GetAllBlockObjectsInPosition(obj)
                    for eachBlocksObject in blocksObjects:
                        result = IntersectGeo(eachBlocksObject, pt.Z)
                        if result is None: 
                            rs.DeleteObject(eachBlocksObject)
                            continue
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
    utils.SaveFunctionData('Geometry-Contour At Pt', [__version__, len(objs), result])
    return result

################################################################################
#UNFILLET
def ArcToPlineCurve(segment):
    pline = segment
    if type(segment) == rc.Geometry.ArcCurve:
        if segment.AngleDegrees < 180:
            ptA1 = segment.PointAtStart + segment.TangentAtStart
            ptB1 = segment.PointAtEnd + segment.TangentAtEnd
            lineA = rc.Geometry.Line(segment.PointAtStart, ptA1)
            lineB = rc.Geometry.Line(segment.PointAtEnd, ptB1)
            result, paramA, paramB = rc.Geometry.Intersect.Intersection.LineLine(lineA, lineB)
            if result:
                ptC = lineA.PointAt(paramA)
                pline = rc.Geometry.PolylineCurve([segment.PointAtStart, ptC, segment.PointAtEnd])
    elif type(segment) == rc.Geometry.NurbsCurve:
        if segment.IsArc(rs.UnitAbsoluteTolerance()):
            result, arc = segment.TryGetArc(rs.UnitAbsoluteTolerance())
            if result:
                if arc.AngleDegrees < 180:
                    ptA0 = arc.StartPoint
                    ptB0 = arc.EndPoint
                    paramA0 = arc.ClosestParameter(ptA0)
                    paramB0 = arc.ClosestParameter(ptB0)
                    ptA1 = ptA0 + arc.TangentAt(paramA0)
                    ptB1 = ptB0 + arc.TangentAt(paramB0)
                    lineA = rc.Geometry.Line(ptA0, ptA1)
                    lineB = rc.Geometry.Line(ptB0, ptB1)
                    result, paramA, paramB = rc.Geometry.Intersect.Intersection.LineLine(lineA, lineB)
                    if result:
                        ptC = lineA.PointAt(paramA)
                        pline = rc.Geometry.PolylineCurve([ptA0, ptC, ptB0])
    return pline

def unfilletObj(obj):
    try:
        rhobj = rs.coercecurve(obj)
        segments = rhobj.DuplicateSegments()
        newSegments = []
        polycurve = rc.Geometry.PolyCurve()
        for i, segment, in enumerate(segments):
            polycurve.AppendSegment(ArcToPlineCurve(segment))
        crvObj = sc.doc.Objects.AddCurve(polycurve)
        rs.SimplifyCurve(crvObj)
        utils.SafeMatchObjectAttributes(crvObj, obj)
        #rs.MatchObjectAttributes(crvObj, obj) #BROKEN
        rs.DeleteObject(obj)
        return crvObj
    except:
        print "Unfillet Failed"
        return None

def Unfillet_Button():
    objs = []
    successList = []
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

if __name__ == "__main__" and utils.IsAuthorized():
    func = rs.GetInteger("func num")
    if func == 0:
        result = IntersectGeoAtPt()
        if result:
            utils.SaveToAnalytics('Geometry-Contour At Pt')
    if func == 1:
        result = Unfillet_Button()
        if result:
            utils.SaveToAnalytics('Geometry-Unfillet')
