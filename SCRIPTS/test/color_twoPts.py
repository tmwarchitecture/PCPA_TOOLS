
import rhinoscriptsyntax as rs

def main():
    
    objs= rs.GetObjects("Select objects to color", preselect = True)
    if objs is None: return
    pt1 = rs.GetPoint("Select first color point")
    if pt1 is None: return
    firstColor = rs.GetColor()
    if firstColor is None: return
    pt2 = rs.GetPoint("Select second color point")
    if pt2 is None: return
    secondColor = rs.GetColor(firstColor)
    if secondColor is None: return
    
    rs.EnableRedraw(False)
    origLine = rs.AddLine(pt1, pt2)
    colorLine = rs.AddLine(firstColor, secondColor)
    
    
    for obj in objs:
        bboxpts = rs.BoundingBox(obj)
        ctrPt = (bboxpts[0] + bboxpts[6]) / 2
        param = rs.CurveClosestPoint(origLine, ctrPt)
        normParam = rs.CurveNormalizedParameter(origLine, param)
        colorParam = rs.CurveParameter(colorLine, normParam)
        finalPt = rs.EvaluateCurve(colorLine, colorParam)
        color = (finalPt.X, finalPt.Y, finalPt.Z)
        rs.ObjectColor(obj, color)    
    
    rs.DeleteObject(colorLine)
    rs.DeleteObject(origLine)
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()
    
