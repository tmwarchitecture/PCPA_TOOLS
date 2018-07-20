import rhinoscriptsyntax as rs
import scriptcontext as sc
from random import shuffle
import utils

def ColorObjsWithGradient2Pt():
    result = True
    try:
        objs= rs.GetObjects("Select objects to color", 1073750077,  preselect = True)
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
        
        try:
            for obj in objs:
                bboxpts = rs.BoundingBox(obj)
                ctrPt = (bboxpts[0] + bboxpts[6]) / 2
                param = rs.CurveClosestPoint(origLine, ctrPt)
                normParam = rs.CurveNormalizedParameter(origLine, param)
                colorParam = rs.CurveParameter(colorLine, normParam)
                finalPt = rs.EvaluateCurve(colorLine, colorParam)
                color = (finalPt.X, finalPt.Y, finalPt.Z)
                rs.ObjectColor(obj, color)    
        except:
            result = False
        rs.DeleteObject(colorLine)
        rs.DeleteObject(origLine)
        rs.EnableRedraw(True)
    except:
        result = False
    utils.SaveFunctionData('colors-Gradient', [firstColor, secondColor, len(objs), result])
    return result

def ColorObjsRandomRange():
    try:
        objs= rs.GetObjects("Select objects to color", 1073750077, preselect = True)
        if objs is None: return
        print "Select First Color"
        firstColor = rs.GetColor()
        if firstColor is None: return
        print "Select Second Color"
        secondColor = rs.GetColor(firstColor)
        if secondColor is None: return
        
        rs.EnableRedraw(False)
        colorLine = rs.AddLine(firstColor, secondColor)
        
        try:
            colors = rs.DivideCurve(colorLine, len(objs)-1)
            
            shuffle(colors)
            
            for i, obj in enumerate(objs):
                rs.ObjectColor(obj, (colors[i].X, colors[i].Y, colors[i].Z))    
        except:
            pass
        rs.DeleteObject(colorLine)
        rs.EnableRedraw(True)
        return True
    except:
        return False

def ColorBySize():
    try:
        objs= rs.GetObjects("Select objects to color", 1073750077, preselect = True)
        if objs is None: return
        print "Select First Color"
        firstColor = rs.GetColor()
        if firstColor is None: return
        print "Select Second Color"
        secondColor = rs.GetColor(firstColor)
        if secondColor is None: return
        
        rs.EnableRedraw(False)
        
        colorLine = rs.AddLine(firstColor, secondColor)
        
        areas = []
        for obj in objs:
            if rs.IsCurve(obj):
                if rs.IsCurveClosed(obj):
                    areas.append(rs.CurveArea(obj)[0])
                else:
                    areas.append(rs.CurveLength(obj))
            elif rs.IsSurface(obj):
                areas.append(rs.SurfaceArea(obj)[0])
            elif rs.IsPolysurface(obj):
                if rs.IsPolysurfaceClosed(obj):
                    areas.append(rs.SurfaceVolume(obj)[0])
            else:
                print "Only curves and surfaces supported"
                return
        
        newAreas = list(areas)
        objAreas = zip(newAreas, objs)
        objAreas.sort()
        objSorted = [objs for newAreas, objs in objAreas]
        
        areas.sort()
        normalParams = utils.RemapList(areas, 0, 1)
        
        colors = []
        for t in normalParams:
            param = rs.CurveParameter(colorLine, t)
            colors.append(rs.EvaluateCurve(colorLine, param))
        
        for i, obj in enumerate(objSorted):
            rs.ObjectColor(obj, (colors[i].X, colors[i].Y, colors[i].Z))    
        
        rs.DeleteObject(colorLine)
        rs.EnableRedraw(True)
        return True
    except:
        return False

def ObjectColorToMaterial():
    try:
        objs = rs.GetObjects("Select objects to transfer color to material", 1073750077, preselect = True)
        if objs is None: return
        for obj in objs:
            color = rs.ObjectColor(obj)
            index = sc.doc.Materials.Add()
            mat = sc.doc.Materials[index]
            mat.DiffuseColor = color
            mat.Name = str(color)
            mat.CommitChanges()
            rs.ObjectMaterialIndex(obj, index)
            rs.ObjectMaterialSource(obj, 1)
        return True
    except:
        return False

if __name__ == "__main__":
    func = rs.GetInteger("Input func number")
    if func == 0:
        result = ColorObjsWithGradient2Pt()
        if result:
            utils.SaveToAnalytics('colors-Gradient')
    elif func == 1:
        result = ColorObjsRandomRange()
        if result:
            utils.SaveToAnalytics('colors-Random Range')
    elif func == 2:
        result = ObjectColorToMaterial()
        if result:
            utils.SaveToAnalytics('colors-Color To Material')
    elif func == 3:
        result = ColorBySize()
        if result:
            utils.SaveToAnalytics('colors-By Size')