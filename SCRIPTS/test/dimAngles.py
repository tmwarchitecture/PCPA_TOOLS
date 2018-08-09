import Rhino as rc
import rhinoscriptsyntax as rs
import scriptcontext as sc

def DimSegmentAngle(segment1, segment2, offset):
    if isinstance(segment1, rc.Geometry.LineCurve) and isinstance(segment2, rc.Geometry.LineCurve):
        pass
    else:
        return None
    
    if segment1.GetLength() < offset*2 or segment2.GetLength() < offset*2:
        offset = min(segment1.GetLength()/2, segment2.GetLength()/2)
    
    seg1EndPt = segment1.PointAtEnd
    
    plane = rc.Geometry.Plane(seg1EndPt, segment2.PointAtEnd, segment1.PointAtStart)
    plane = rs.WorldXYPlane()
    
    seg1DimPtB = segment1.PointAtLength(segment1.GetLength() - offset*.7)
    seg2DimPtB = segment2.PointAtLength(offset*.7)
    
    extPt1 = seg1EndPt
    extPt2 = seg1EndPt
    dirPt1 = seg1DimPtB
    dirPt2 = seg2DimPtB
    
    avgPt = (seg1DimPtB + seg2DimPtB) / 2 #GOOD
    vec = rs.VectorCreate(avgPt, seg1EndPt)
    vec.Unitize()
    dimLinePt = rc.Geometry.Point3d.Add(seg1EndPt, vec*offset)
    
    dim = rc.Geometry.AngularDimension.Create(sc.doc.DimStyles.Current.Id, plane, extPt1, extPt2, dirPt1, dirPt2, dimLinePt)
    dim.TextPosition = rc.Geometry.Point2d(offset, offset)
    return sc.doc.Objects.AddAngularDimension(dim)

def DimAngles(obj, offset):
    curve = rs.coercecurve(obj)
    segments = curve.DuplicateSegments()
    for i, segment in enumerate(segments):
        if i == len(segments)-1:
            break
        DimSegmentAngle(segments[i], segments[i+1], offset)  
        print ""
    if rs.IsCurveClosed(obj):
        DimSegmentAngle(segments[-1], segments[0], offset)    

def DimAngles_Button():
    objs = rs.GetObjects("Select polylines to dimension the angles of", rs.filter.curve, preselect = True)
    if objs is None: return
    
    defaultNumber = 25
    offset = rs.GetInteger("Offset distance (inches)", defaultNumber, minimum = 1)
    if offset is None: return
    
    for obj in objs:
        DimAngles(obj, offset)
        

if __name__ == "__main__":
    DimAngles_Button()