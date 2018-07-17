import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc

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
        rs.JoinCurves(xCurves)
    except:
        pass
    for curve in xCurves:
        pass
        finalCurve = sc.doc.Objects.AddCurve(curve)
        rs.MatchObjectAttributes(finalCurve, obj)
    sc.doc.Views.Redraw()

if __name__ == "__main__":
    objs = rs.GetObjects()
    levels = [8, 18, 30]
    
    for obj in objs:
        for level in levels:
            IntersectGeo(obj, level)
    #circle = Rhino.Geometry.Circle(plane, 999999)
    #negShape = Rhino.Geometry.Cylinder(circle, 999999)
    #negShapeBrep = negShape.ToBrep(True, True)
    #negShapeGeo = sc.doc.Objects.AddBrep(negShapeBrep)
    #
    #splitSrfs = rs.SplitBrep(brep, negShapeGeo)