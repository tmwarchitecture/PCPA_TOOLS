import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math

def ChamferCorners(segments, closed):
    chamfers = []
    
    
    for i in range(len(segments)-1):
        pt1 = segments[i].PointAtEnd
        pt2 = segments[i+1].PointAtStart
        chamfers.append(rc.Geometry.LineCurve(pt1, pt2))
    if closed:
        pt1 = segments[-1].PointAtEnd
        pt2 = segments[0].PointAtStart
        chamfers.append(rc.Geometry.LineCurve(pt1, pt2))
    
    
    allCurves = []
    for segment in segments:
        allCurves.append(segment)
    
    allCurves += chamfers
    
    pline = rc.Geometry.Curve.JoinCurves(allCurves)
    
    return pline

def NotchCorners(segments, closed, angle1, angle2):
    angle1 = math.radians(angle1)
    angle2 = math.radians(180-angle2)
    notches = []
    
    for i in range(len(segments)-1):
        pt1 = segments[i].PointAtEnd
        tan1 = segments[i].TangentAtEnd
        tan1.Rotate(angle1, rc.Geometry.Vector3d(0,0,1))
        line1End = rc.Geometry.Point3d.Add(pt1, tan1)
        line1 = rc.Geometry.Line(pt1, line1End)
        
        pt2 = segments[i+1].PointAtStart
        tan2 = segments[i+1].TangentAtStart
        tan2.Rotate(angle2, rc.Geometry.Vector3d(0,0,1))
        line2End = rc.Geometry.Point3d.Add(pt2, tan2)
        line2 = rc.Geometry.Line(pt2, line2End)
        
        result = rc.Geometry.Intersect.Intersection.LineLine(line1, line2)
        interPt = line1.PointAt(result[1])
        
        notch = rc.Geometry.Polyline([pt1, interPt, pt2])
        notch = notch.ToPolylineCurve()
        notches.append(notch)
    
    if closed:
        pt1 = segments[-1].PointAtEnd
        tan1 = segments[-1].TangentAtEnd
        tan1.Rotate(angle1, rc.Geometry.Vector3d(0,0,1))
        line1End = rc.Geometry.Point3d.Add(pt1, tan1)
        line1 = rc.Geometry.Line(pt1, line1End)
        
        pt2 = segments[0].PointAtStart
        tan2 = segments[0].TangentAtStart
        tan2.Rotate(angle2, rc.Geometry.Vector3d(0,0,1))
        line2End = rc.Geometry.Point3d.Add(pt2, tan2)
        line2 = rc.Geometry.Line(pt2, line2End)
        
        result = rc.Geometry.Intersect.Intersection.LineLine(line1, line2)
        interPt = line1.PointAt(result[1])
        
        notch = rc.Geometry.Polyline([pt1, interPt, pt2])
        notch = notch.ToPolylineCurve()
        notches.append(notch)
    
    
    allCurves = []
    for segment in segments:
        allCurves.append(segment)
    
    allCurves += notches
    
    pline = rc.Geometry.Curve.JoinCurves(allCurves)
    
    return pline

def RetractCorners(pline, dist1, dist2):
    segments = pline.DuplicateSegments()
    #####
    for i in range(len(segments)-1):
        seg1Length = segments[i].GetLength()
        param1 = segments[i].LengthParameter(seg1Length-dist1)
        pt1 = segments[i].PointAt(param1[1])
        
        interval1 = rc.Geometry.Interval(0, param1[1])
        trimmed1 = segments[i].Trim(interval1)
        segments[i] = trimmed1
        
        param2 = segments[i+1].LengthParameter(dist2)
        pt2 = segments[i+1].PointAt(param2[1])
        
        interval2 = rc.Geometry.Interval(param2[1], 1)
        segments[i+1] = segments[i+1].Trim(interval2)
    
    #####
    if pline.IsClosed:
        seg1Length = segments[-1].GetLength()
        param1 = segments[-1].LengthParameter(seg1Length-dist1)
        pt1 = segments[-1].PointAt(param1[1])
        
        interval1 = rc.Geometry.Interval(0, param1[1])
        trimmed1 = segments[-1].Trim(interval1)
        segments[-1] = trimmed1
        
        param2 = segments[0].LengthParameter(dist2)
        pt2 = segments[0].PointAt(param2[1])
        
        endParam = segments[0].Domain[1]
        interval2 = rc.Geometry.Interval(param2[1], endParam)
        segments[0] = segments[0].Trim(interval2)
    
    return segments

def ChamferEdges(rhobj, dist1, dist2):
    segments = RetractCorners(rhobj, dist1, dist2)
    newPlines = ChamferCorners(segments, rhobj.IsClosed)
    
    finalSegments = []
    for pline in newPlines:
        finalSegments.append(sc.doc.Objects.AddCurve(pline))
    
    return finalSegments

def NotchCurve(rhobj, dist1, angle1, dist2, angle2):
    segments = RetractCorners(rhobj, dist1, dist2)
    
    newPlines = NotchCorners(segments, rhobj.IsClosed, angle1, angle2)
    
    finalSegments = []
    for pline in newPlines:
        finalSegments.append(sc.doc.Objects.AddCurve(pline))
    
    return finalSegments

def ChamferButton():
    objs = rs.GetObjects("Select curves to chamfer", preselect = True)
    if objs is None: return
    
    dist1 = rs.GetReal('Distance 1', 30)
    if dist1 is None: return
    dist2 = rs.GetReal('Distance 2', 60)
    if dist2 is None: return
    
    finalCurves = []
    for obj in objs:
        rhobj = rs.coercecurve(obj)
        finalCurves.append(ChamferEdges(rhobj, dist1, dist2))
        rs.DeleteObject(obj)
    
    return finalCurves

def NotchButton():
    objs = rs.GetObjects("Select curves to notch", preselect = True)
    if objs is None: return
    
    dist1 = rs.GetReal('Distance 1', 30)
    if dist1 is None: return
    angle1 = rs.GetReal('Angle 1', 90)
    if angle1 is None: return
    dist2 = rs.GetReal('Distance 2', 60)
    if dist2 is None: return
    angle2 = rs.GetReal('Angle 2', 90)
    if angle2 is None: return
    
    finalCurves = []
    for obj in objs:
        rhobj = rs.coercecurve(obj)
        finalCurves.append(NotchCurve(rhobj, dist1, angle1, dist2, angle2))
        rs.DeleteObject(obj)
    
    return finalCurves

def main():
    func = rs.GetInteger("Select Function")
    if func is None: return
    if func == 0:
        ChamferButton()
    elif func == 1:
        NotchButton()

main()