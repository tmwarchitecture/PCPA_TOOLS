import rhinoscriptsyntax as rs
import scriptcontext as sc
from random import shuffle
import utils

def ColorObjsWithGradient2Pt():
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

def ColorObjsRandomRange():
    objs= rs.GetObjects("Select objects to color", preselect = True)
    if objs is None: return
    print "Select First Color"
    firstColor = rs.GetColor()
    if firstColor is None: return
    print "Select Second Color"
    secondColor = rs.GetColor(firstColor)
    if secondColor is None: return
    
    rs.EnableRedraw(False)
    colorLine = rs.AddLine(firstColor, secondColor)
    
    colors = rs.DivideCurve(colorLine, len(objs)-1)
    
    shuffle(colors)
    
    for i, obj in enumerate(objs):
        rs.ObjectColor(obj, (colors[i].X, colors[i].Y, colors[i].Z))    
    
    rs.DeleteObject(colorLine)
    rs.EnableRedraw(True)

def ColorBySize():
    objs= rs.GetObjects("Select objects to color", preselect = True)
    if objs is None: return
    print "Select First Color"
    firstColor = rs.GetColor()
    if firstColor is None: return
    print "Select Second Color"
    secondColor = rs.GetColor(firstColor)
    if secondColor is None: return
    
    rs.EnableRedraw(False)
    colorLine = rs.AddLine(firstColor, secondColor)
    
    #This should be replaced by remapped numbers instead of evenly divide
    colors = rs.DivideCurve(colorLine, len(objs)-1)
    
    areas = []
    for obj in objs:
        if rs.IsCurve(obj):
            areas.append(rs.CurveArea(obj)[0])
        elif rs.IsSurface(obj):
            areas.append(rs.SurfaceArea(obj)[0])
        else:
            print "Only curves and surfaces supported"
            return
    
    objAreas = zip(areas, objs)
    objAreas.sort()
    objSorted = [objs for areas, objs in objAreas]
    
    for i, obj in enumerate(objSorted):
        rs.ObjectColor(obj, (colors[i].X, colors[i].Y, colors[i].Z))    
    
    rs.DeleteObject(colorLine)
    rs.EnableRedraw(True)

def ObjectColorToMaterial():
    objs = rs.GetObjects("Select objects to transfer color to material", preselect = True)
    for obj in objs:
        color = rs.ObjectColor(obj)
        index = sc.doc.Materials.Add()
        mat = sc.doc.Materials[index]
        mat.DiffuseColor = color
        mat.Name = str(color)
        mat.CommitChanges()
        rs.ObjectMaterialIndex(obj, index)
        rs.ObjectMaterialSource(obj, 1)

if __name__ == "__main__":
    func = rs.GetInteger("Input func number")
    if func == 0:
        ColorObjsWithGradient2Pt()
        utils.SaveToAnalytics('colors-Color Objs With Gradient 2Pt')
    elif func == 1:
        ColorObjsRandomRange()
        utils.SaveToAnalytics('colors-Color Objs Random Range')
    elif func == 2:
        ObjectColorToMaterial()
        utils.SaveToAnalytics('colors-Object Color To Material')
    elif func == 3:
        ColorBySize()
        utils.SaveToAnalytics('colors-Color By Size')