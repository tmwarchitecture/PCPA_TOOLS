import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math

import utils

def GetAngleBetween2Segments(segment1, segment2, plane, internal = False):
    """
    Compares angle of 2 segments, on a plane.
    inputs:
        segment1 (curve)
        segment2 (curve)
        plane (plane)
        internal = True (bool): Internal or external angles
    returns:
        angle (float)
    """
    seg1EndTan = segment1.TangentAtEnd
    seg1EndTan.Reverse()
    seg2StTan = segment2.TangentAtStart
    angle = seg1EndTan.VectorAngle(seg1EndTan, seg2StTan, plane)
    if internal:
        return 360-math.degrees(angle)
    else:
        return math.degrees(angle)

def GetCornerAngles(obj):
    internalCornerAngles = []
    rhobj = rs.coercecurve(obj)
    segments = rhobj.DuplicateSegments()
    plane = rs.WorldXYPlane()
    for i in range(1, len(segments)):
        internalCornerAngles.append(GetAngleBetween2Segments(segments[i-1], segments[i], plane))
    if rhobj.IsClosed:
        internalCornerAngles.append(GetAngleBetween2Segments(segments[-1], segments[0], plane))
    
    return internalCornerAngles

def GetSegmentLengths(obj):
    rhobj = rs.coercecurve(obj)
    segments = rhobj.DuplicateSegments()
    distances = []
    for segment in segments:
        distances.append(segment.GetLength())
    return distances

def ForceToMultipleOf(numbers, multiple):
    newNumbers = []
    dec = str(multiple)
    decPlaces = int(dec[::-1].find('.'))
    for number in numbers:
        newNumber = round(number/multiple)*multiple
        if newNumber < multiple:
            newNumber = multiple
        roundedNumber = round(newNumber, decPlaces)
        newNumbers.append(roundedNumber)
    return newNumbers

def RotatePoint(distance, centerPt, refPt, angle, axis):
    """
    Rotates pt around a point to a specific angle, relative to another
    rotates CCW
    """
    prevSegment = rs.VectorCreate(refPt, centerPt)
    prevSegment.Rotate(math.radians(angle), axis)
    prevSegment.Unitize()
    
    finalPt = rc.Geometry.Point3d.Add(centerPt, prevSegment * distance)
    return finalPt

def ChangeVertexAngles(obj, fixedAngles, fixedLengths):
    """
    rotates polyline vertices to the new angles
    """
    rhobj = rs.coercecurve(obj)
    segments = rhobj.DuplicateSegments()
    ctrlPts = []
    for segment in segments:
        ctrlPts.append(segment.PointAtStart)
    
    newPts = []
    axis = rc.Geometry.Vector3d(0,0,1)
    
    
    newPts.append(ctrlPts[0])
    firstSegVec = rc.Geometry.Vector3d(ctrlPts[1] - ctrlPts[0])
    firstSegVec.Unitize()
    secondPt = ctrlPts[0].Add(ctrlPts[0], firstSegVec * fixedLengths[0])
    #secondPt = rc.Geometry.Point3d.Add(ctrlPts[0], firstSegVec * fixedLengths[0])
    newPts.append(secondPt)
    
    for i in range(1, len(ctrlPts)-1):
        newPts.append(RotatePoint(fixedLengths[i], newPts[-1], newPts[-2], fixedAngles[i-1], axis))
    
    if rhobj.IsClosed:
        newPts.append(RotatePoint(fixedLengths[-1], newPts[-1], newPts[-2], fixedAngles[-2], axis))
        lineLast = rc.Geometry.Line(newPts[-2], newPts[-1])
        lineFirst = rc.Geometry.Line(newPts[1], newPts[0])
        intersection = rc.Geometry.Intersect.Intersection.LineLine(lineLast, lineFirst)
        pt = lineLast.PointAt(intersection[1])
        newPts[0] = pt
        newPts[-1] = pt
    else:
        newPts.append(RotatePoint(fixedLengths[-1], newPts[-1], newPts[-2], fixedAngles[-1], axis))
    
    return rc.Geometry.Polyline(newPts)

def Rectify_AngleFirst(obj, angleMultiple, lengthMultiple):
    """
    Rebuilds a polyline with exact angles and lengths. Angles have priority
    input:
        obj (polyline)
        angleMultiple (float): Multiple to round to
        lengthMultiple (float): Length to round to (0 == no rounding)
    returns:
        polyline (guid)
    """
    angles = GetCornerAngles(obj)
    if angleMultiple != 0:
        fixedAngles = ForceToMultipleOf(angles, angleMultiple)
    else:
        fixedAngles = angles
    
    lengths = GetSegmentLengths(obj)
    if lengthMultiple != 0:
        fixedLengths = ForceToMultipleOf(lengths, lengthMultiple)
    else:
        fixedLengths = lengths
    
    newPline = ChangeVertexAngles(obj, fixedAngles, fixedLengths)
    id = sc.doc.Objects.AddPolyline(newPline)
    sc.doc.Views.Redraw()
    return id

def Rectify_AngleFirst_Button():
    objs = rs.GetObjects("Select polylines to rectify", rs.filter.curve, preselect = True)
    if objs is None: return
    
    if 'geometry-angleMultiple' in sc.sticky:
        angleDefault = sc.sticky['geometry-angleMultiple']
    else:
        angleDefault = 45
    
    if 'geometry-lengthMultiple' in sc.sticky:
        lengthDefault = sc.sticky['geometry-lengthMultiple']
    else:
        lengthDefault = 1
    
    angleMultiple = rs.GetReal("Round angle to multiples of", angleDefault)
    if angleMultiple is None: return
    sc.sticky['geometry-angleMultiple'] = angleMultiple
    
    
    lengthMultiple = rs.GetReal("Round length to multiples of", lengthDefault)
    if lengthMultiple is None: return
    sc.sticky['geometry-lengthMultiple'] = lengthMultiple
    
    for obj in objs:
        try:
            rs.SimplifyCurve(obj)
            newLine = Rectify_AngleFirst(obj, angleMultiple, lengthMultiple)
            utils.SaveToAnalytics('Geometry-Rectify')
            result = True
        except:
            result = False
            print "Rectify failed"
        utils.SaveFunctionData('Geometry-Rectify', [angleMultiple, lengthMultiple,  str([(pt.X, pt.Y, pt.Z) for pt in rs.CurveEditPoints(obj)]), result])
        

if __name__ == "__main__":
    Rectify_AngleFirst_Button()