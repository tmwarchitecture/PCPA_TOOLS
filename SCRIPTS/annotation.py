import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import layers
import utils

def AreaTag(obj, decPlaces):
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
            areaTag = rs.AddText(areaText, rs.CurveAreaCentroid(obj)[0], justification = 131074)
            
            #Change layers
            hostLayer = layers.AddLayerByNumber(8103, False)
            rs.ObjectLayer(areaTag, layers.GetLayerNameByNumber(8103))
            return area
        else: 
            print "Curve not closed"
            return 0
    else:
        print "Curve not planar"
        return 0

def AddAreaTag():
    objs = rs.GetObjects("Select curves to add area tag", preselect = True)
    if objs is None: return
    
    decPlaces = rs.GetInteger("Number of decimal places", 0, maximum = 8)
    if decPlaces is None: return
    
    rs.EnableRedraw(False)
    total = 0
    for obj in objs:
        try:
            total += AreaTag(obj, decPlaces)
        except:
            pass
    print 'Cumulative Area = ' + str(total)
    rs.EnableRedraw(True)

if __name__=="__main__":
    func = rs.GetInteger("Func num")
    if func == 0:
        AddAreaTag()
        utils.SaveToAnalytics('IO-Add Area Tag')