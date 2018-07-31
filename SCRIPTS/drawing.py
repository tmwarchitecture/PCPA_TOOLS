import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import layers
import utils
import standards

###############################################################################
def AreaTag(obj, decPlaces):
    try:
        if rs.IsCurvePlanar(obj):
            if rs.IsCurveClosed(obj):
                #get area
                if rs.UnitSystem() == 8:
                    area = rs.CurveArea(obj)[0]*0.0069444444444444
                    areaText = utils.RoundNumber(area, decPlaces) + " SF"
                else:
                    print "WARNING: Your units are not in inches"
                    area = rs.CurveArea(obj)[0]
                    areaText = area + ' ' + rs.UnitSystemName(False, True, True)
                
                #add text tag
                dimStyle = sc.doc.DimStyles.FindName('PCPA_12')
                
                if dimStyle is not None:
                    textHeight = dimStyle.TextHeight
                    areaTag = rs.AddText(areaText, rs.CurveAreaCentroid(obj)[0], height = textHeight, justification = 131074)
                else:
                    areaTag = rs.AddText(areaText, rs.CurveAreaCentroid(obj)[0], height = 1, justification = 131074)
                
                #Change layers
                hostLayer = layers.AddLayerByNumber(8103, False)
                rs.ObjectLayer(areaTag, layers.GetLayerNameByNumber(8103))
                return [area, True]
            else: 
                print "Curve not closed"
                return [0, False]
        else:
            print "Curve not planar"
            return [0, False]
    except:
        return [0, False]

def AddAreaTag():
    objs = rs.GetObjects("Select curves to add area tag", rs.filter.curve, preselect = True)
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
            currentArea,rc = AreaTag(obj, decPlaces)
            utils.SaveFunctionData('Drawing-Add Area Tag', [rs.DocumentPath(), rs.DocumentName(), rs.ObjectLayer(obj), rs.ObjectDescription(obj), str([(pt.X, pt.Y, pt.Z) for pt in rs.CurveEditPoints(obj)]), rs.CurrentDimStyle(), currentArea, decPlaces, rc])
            total += currentArea
        except:
            print "Failed here"
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
