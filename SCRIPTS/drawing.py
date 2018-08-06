import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rc
import Rhino
import math

import layers
import utils
import standards


def AddCoordinateTag(obj):
    dots = []
    if rs.IsCurve(obj):
        pts = rs.CurveEditPoints(obj)
    elif rs.IsSurface(obj):
        pts = rs.SurfaceEditPoints(obj)
    elif rs.IsBrep(obj):
        srfs = rs.ExplodePolysurfaces(obj)
        pts = []
        for srf in srfs:
            pts+=rs.SurfaceEditPoints(srf)
        rs.DeleteObjects(srfs)
    try:
        pts
    except:
        return
    for pt in pts:
        dots.append(rs.AddTextDot('X: '+str(pt.X)+'\nY: '+str(pt.Y)+'\nZ: ' +str( pt.Z), pt))
    return dots

def AddCoordinateTag_Button():
    objs = rs.GetObjects("Select objects to add coordinates to", 1073741853 ,preselect = True)
    if objs is None: return
    
    dotGroup = rs.AddGroup('DotGroup')
    rs.EnableRedraw(False)
    for obj in objs:
        try:
            rs.AddObjectsToGroup(AddCoordinateTag(obj), dotGroup)
            utils.SaveFunctionData('Drawing-Add Coordinate Tag', [len(objs), True])
        except:
            utils.SaveFunctionData('Drawing-Add Coordinate Tag', [len(objs), False])
    rs.EnableRedraw(True)

###############################################################################
def HorizPlaneFromSurface(srf):
    rhsrf = rs.coercesurface(srf)
    centerPoint = utils.FindMostDistantPointOnSrf(srf)
    u, v = rs.SurfaceClosestPoint(srf, centerPoint)
    origPlane = rhsrf.FrameAt(u,v)[1]
    if abs(origPlane.Normal.Z) == 1:
        #SURFACE HORIZONTAL
        plane = rs.WorldXYPlane()
        plane.Origin = centerPoint
        return plane
    else:
        #SURFACE NOT HORIZONTAL
        upVec = utils.GetUphillVectorFromPlane(srf)
        ptUp = rc.Geometry.Point3d.Add(centerPoint, upVec)
        line1 = rc.Geometry.Line(centerPoint, ptUp)
        ptY = rc.Geometry.Point3d.Add(centerPoint, origPlane.YAxis)
        line2 = rc.Geometry.Line(centerPoint, ptY)
        angle = math.radians(min(rs.Angle2(line1, line2)))
        origPlane.Rotate(angle, origPlane.Normal, centerPoint)
        return origPlane

def AreaTag(obj, decPlaces):
    try:
        rhsrf = rs.coercesurface(obj)
        if rs.IsCurve(obj):
            if rs.IsCurvePlanar(obj) == False:
                return [0, False]
            if rs.IsCurveClosed(obj) == False:
                return [0, False]
        
        #get area
        if rs.UnitSystem() == 8:
            if rs.IsCurve(obj):
                area = rs.CurveArea(obj)[0]*0.0069444444444444
            else:
                area = rs.Area(obj)*0.0069444444444444
            areaText = utils.RoundNumber(area, decPlaces) + " SF"
        else:
            print "WARNING: Your units are not in inches"
            area = rs.CurveArea(obj)[0]
            areaText = area + ' ' + rs.UnitSystemName(False, True, True)
        
        #add annotation style
        dimStyle = sc.doc.DimStyles.FindName('PCPA_12')
        
        ###########################################################################
        #CURVES
        if rs.IsCurve(obj):
            if utils.IsRectangle(obj)[0]:
                #RECTANGLES
                srf = rs.AddPlanarSrf(obj)
                plane = HorizPlaneFromSurface(srf)
                rs.DeleteObject(srf)
            else:
                #OTHER CURVES
                srf = rs.AddPlanarSrf(obj)
                plane = HorizPlaneFromSurface(srf)
                rs.DeleteObject(srf)
        ###########################################################################
        #HATCHES
        elif rs.IsHatch(obj):
            rhobj = rs.coercegeometry(obj)
            boundaryCrvs = []
            crvs = rhobj.Get3dCurves(False)
            for crv in crvs:
                boundaryCrvs.append(crv)
            for crv in rhobj.Get3dCurves(True):
                boundaryCrvs.append(crv)
            srf = sc.doc.Objects.AddBrep(rc.Geometry.Brep.CreatePlanarBreps(boundaryCrvs)[0])
            plane = HorizPlaneFromSurface(srf)
            rs.DeleteObject(srf)
        ###########################################################################
        #SURFACES
        elif rs.IsSurface(obj):
            plane = HorizPlaneFromSurface(obj)
        
        ###########################################################################
        #OTHER/ERROR
        else:
            pts = rs.BoundingBox(obj)
            centerPoint = (pts[0] + pts[6]) / 2
        
        
        if dimStyle is not None:
            textHeight = dimStyle.TextHeight
            areaTag = rs.AddText(areaText, plane, height = textHeight, justification = 131074)
        else:
            areaTag = rs.AddText(areaText, plane, height = 1, justification = 131074)
        
        #Change layers
        hostLayer = layers.AddLayerByNumber(8103, False)
        rs.ObjectLayer(areaTag, layers.GetLayerNameByNumber(8103))
        return [area, True]
    except:
        return [0, False]

def AddAreaTag():
    objs = rs.GetObjects("Select curves, hatches, or surfaces to add area tag", 65548, preselect = True)
    if objs is None: return
    
    decPlaces = rs.GetInteger("Number of decimal places", 0, maximum = 8)
    if decPlaces is None: return
    
    #Load Anno style if it doesnt exist already
    if sc.doc.DimStyles.FindName('PCPA_12') is None:
        standards.LoadStyles()
    
    rs.EnableRedraw(False)
    total = 0
    for obj in objs:
        try:
            currentArea,result = AreaTag(obj, decPlaces)
            utils.SaveFunctionData('Drawing-Add Area Tag', [rs.DocumentName(), rs.ObjectLayer(obj), rs.ObjectDescription(obj), rs.CurrentDimStyle(), currentArea, decPlaces, result])
            total += currentArea
        except:
            pass
    print 'Cumulative Area = ' + str(total)
    
    rs.EnableRedraw(True)

###############################################################################
def dimensionPline(pline, offsetDist):
    try:
        if rs.IsCurvePlanar(pline):
            pass
        else:
            print "Curve must be planar"
            return 
        
        segments = []
        dimGroup = rs.AddGroup("Pline Dims")
        
        dir = rs.ClosedCurveOrientation(pline)
        if dir == -1:
            rs.ReverseCurve(pline)
        
        normal = rs.CurvePlane(pline).ZAxis
        
        segments = rs.ExplodeCurves(pline)
        if len(segments)<1:
            segments = [rs.CopyObject(pline)]
        for seg in segments:
            if rs.IsLine(seg):
                endPt = rs.CurveEndPoint(seg)
                stPt = rs.CurveStartPoint(seg)
                tanVec = rs.VectorCreate(stPt, endPt)
                offsetVec = rs.VectorRotate(tanVec, 90, normal)
                offsetVec = rs.VectorUnitize(offsetVec)
                offsetVec = rs.VectorScale(offsetVec, offsetDist)
                offsetPt = rs.VectorAdd(stPt, offsetVec)
                dim = rs.AddAlignedDimension(stPt, endPt, rs.coerce3dpoint(offsetPt), 'PCPA_12')
                rs.AddObjectToGroup(dim, dimGroup)
        rs.DeleteObjects(segments)
        result = True
    except:
        result = False
    return [dimGroup, result]

def dimensionPline_Button():
    objects = rs.GetObjects("Select Curves to Dimension", filter = 4, preselect = True)
    if objects is None:return
    
    if 'dimPline-dist' in sc.sticky:
        distDefault = sc.sticky['dimPline-dist']
    else:
        distDefault = 60
    
    offsetDist = rs.GetInteger('Dimension offset distance (in.)', distDefault)
    if offsetDist is None: return
    
    sc.sticky['dimPline-dist'] = offsetDist
    
    #Load Anno style if it doesnt exist already
    if sc.doc.DimStyles.FindName('PCPA_12') is None:
        standards.LoadStyles()
    
    try:
        layers.AddLayerByNumber(8101)
        layerName = layers.GetLayerNameByNumber(8101)
        rs.CurrentLayer(layerName)
    except:
        pass
    
    
    rs.EnableRedraw(False)
    for obj in objects:
        if rs.IsCurve(obj):
            try:
                group, rc = dimensionPline(obj, offsetDist)
                utils.SaveFunctionData('Drawing-Dim Pline', [rs.DocumentPath(), rs.DocumentName(), rs.ObjectLayer(obj), rs.CurrentDimStyle(), offsetDist, rc])
            except:
                print "Unknown Error"
        else:
            print "Not a polyline"
    rs.EnableRedraw(True)

if __name__=="__main__":
    func = rs.GetInteger("Func num")
    if func == 0:
        AddAreaTag()
        utils.SaveToAnalytics('Drawing-Add Area Tag')
    elif func == 1:
        dimensionPline_Button()
        utils.SaveToAnalytics('Drawing-Dim Pline')
    elif func == 2:
        AddCoordinateTag_Button()
        utils.SaveToAnalytics('Drawing-Add Coordinate Tag')
