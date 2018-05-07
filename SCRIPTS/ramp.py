import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc

def GetRampRuns(path, width):
    topOffset = 12
    btmOffset = 12
    newPath = rs.CopyObject(path)
    segments = rs.ExplodeCurves(newPath, True)
    stPt1 = rs.CurveStartPoint(segments[0])
    stPt2 = rs.CurveStartPoint(segments[0])
    vec = rs.CurveTangent(path, 0)
    rs.VectorUnitize(vec)
    vec = rs.VectorScale(vec, width/2)
    
    vecSide1 = rs.VectorRotate(vec, 90, (0,0,1))
    vecSide2 = rs.VectorRotate(vec, -90, (0,0,1))
    
    ptSide1 = rs.MoveObject(stPt1, vecSide1)
    ptSide2 = rs.MoveObject(stPt2, vecSide2)
    
    offsetCrv1 = rs.OffsetCurve(path, ptSide1, width/2)
    offsetCrv2 = rs.OffsetCurve(path, ptSide2, width/2)
    
    pts1 = rs.CurveEditPoints(offsetCrv1)
    pts2 = rs.CurveEditPoints(offsetCrv2)
    del pts1[0]
    del pts2[0]
    
    nextSegOffsetStPt = stPt1
    
    landingLines = []
    
    #Entering Loop
    for i, segment in enumerate(segments):
        beginningPt = rs.EvaluateCurve(segment, rs.CurveClosestPoint(segment, nextSegOffsetStPt))
        crossVec = rs.VectorScale(rs.VectorCreate(beginningPt, nextSegOffsetStPt), 2)
        
        widthStPt = rs.CopyObject(nextSegOffsetStPt)
        widthEndPt = rs.MoveObject(nextSegOffsetStPt, crossVec)
        
        closestPt1Param = rs.CurveClosestPoint(segment, pts1[i])
        closestPt1 = rs.EvaluateCurve(path, closestPt1Param)
        
        closestPt2Param = rs.CurveClosestPoint(segment, pts2[i])
        closestPt2 = rs.EvaluateCurve(path, closestPt2Param)
        
        if rs.Distance(closestPt2, beginningPt) > rs.Distance(closestPt1, beginningPt):
            nextSegOffsetStPt = pts1[i]
        else:
            nextSegOffsetStPt = pts2[i]
        
        if rs.Distance(nextSegOffsetStPt, widthStPt) < rs.Distance(nextSegOffsetStPt, widthEndPt):
            stLine = rs.AddLine(widthStPt, widthEndPt)
            shortVec = rs.VectorCreate(widthEndPt, widthStPt)
            pt4 = rs.CopyObject(nextSegOffsetStPt, shortVec)
            endLine = rs.AddLine(nextSegOffsetStPt, pt4)
            
            if i == 0:
                pass
            else:
                longVec = rs.VectorReverse(rs.VectorCreate(widthStPt, nextSegOffsetStPt))
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), btmOffset)
                stLine = rs.MoveObject(stLine, longVec)
            if i == len(segments)-1:
                pass
            else:
                longVec = rs.VectorCreate(widthStPt, nextSegOffsetStPt)
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), topOffset)
                endLine = rs.MoveObject(endLine, longVec)
        else:
            stLine = rs.AddLine(widthEndPt, widthStPt)
            shortVec = rs.VectorCreate(widthStPt, widthEndPt)
            pt4 = rs.CopyObject(nextSegOffsetStPt, shortVec)
            endLine = rs.AddLine(nextSegOffsetStPt, pt4)
            
            if i == 0:
                pass
            else:
                longVec = rs.VectorReverse(rs.VectorCreate(widthEndPt, nextSegOffsetStPt))
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), btmOffset)
                stLine = rs.MoveObject(stLine, longVec)
            if i == len(segments)-1:
                pass
            else:
                longVec = rs.VectorCreate(widthEndPt, nextSegOffsetStPt)
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), topOffset)
                endLine = rs.MoveObject(endLine, longVec)
        
        #Done
        landingLines.append([stLine, endLine])
        
        #Cleanup
        rs.DeleteObject(widthStPt)
        rs.DeleteObject(pt4)
        rs.DeleteObject(widthEndPt)
    
    #Cleanup
    rs.DeleteObject(ptSide1)
    rs.DeleteObject(ptSide2)
    rs.DeleteObjects(segments)
    rs.DeleteObject(offsetCrv1)
    rs.DeleteObject(offsetCrv2)
    return landingLines

def GetRampLandings(allLines):
    landingGeo = []
    rs.DeleteObject(allLines[0])
    rs.DeleteObject(allLines[-1])
    del allLines[0]
    del allLines[-1]
    
    for i in range(0, len(allLines), 2):
        #TOP LINE
        stPt = rs.CurveStartPoint(allLines[i])
        endPt = rs.CurveEndPoint(allLines[i])
        tanVec = rs.CurveTangent(allLines[i], 0)
        
        perpVec = rs.VectorRotate(tanVec, 90, (0,0,1))
        
        stPtOffset = rs.CopyObject(stPt, perpVec)
        endPtOffset = rs.CopyObject(endPt, perpVec)
        stLine = rs.AddLine(stPt, stPtOffset)
        endLine = rs.AddLine(endPt, endPtOffset)
        
        #Bottom line
        allLines[i]
        stPtBtm = rs.CurveStartPoint(allLines[i+1])
        endPtBtm = rs.CurveEndPoint(allLines[i+1])
        tanVecBtm = rs.CurveTangent(allLines[i+1], 0)
        
        perpVecBtm = rs.VectorRotate(tanVecBtm, -90, (0,0,1))
        
        stPtOffsetBtm = rs.CopyObject(stPtBtm, perpVecBtm)
        endPtOffsetBtm = rs.CopyObject(endPtBtm, perpVecBtm)
        stLineBtm = rs.AddLine(stPtBtm, stPtOffsetBtm)
        endLineBtm = rs.AddLine(endPtBtm, endPtOffsetBtm)
        
        #Intersection
        stInter = rs.AddPoint(rs.LineLineIntersection(stLineBtm, stLine)[0])
        endInter = rs.AddPoint(rs.LineLineIntersection(endLineBtm, endLine)[0])
        
        landingPts = [stPt, endPt, endInter, endPtBtm, stPtBtm, stInter, stPt]
        landingCrv = rs.AddPolyline(landingPts)
        landingGeo.append(rs.AddPlanarSrf(landingCrv))
        rs.DeleteObject(landingCrv)
        rs.DeleteObject(stLine)
        rs.DeleteObject(endLine)
        rs.DeleteObject(stLineBtm)
        rs.DeleteObject(endLineBtm)
        rs.DeleteObjects([stPtOffset, endPtOffset, stPtOffsetBtm, endPtOffsetBtm, stInter, endInter])
    rs.DeleteObjects(allLines)
    return landingGeo

def Ramp_HeightSlope(path, width, height, slope):
    rs.EnableRedraw(False)
    runs = GetRampRuns(path, width)
    
    runGeo = []
    vertMove = (0,0,0)
    
    for run in runs:
        length = rs.Distance(rs.CurveStartPoint(run[0]), rs.CurveStartPoint(run[1]))
        
        stHeight = vertMove
        vertMove = (0,0,length * slope)
        
        rs.MoveObject(run[-1], vertMove)
        rs.MoveObjects(run, stHeight)
        
        vertMove = rs.VectorAdd(stHeight, vertMove)
        
        srf = rs.AddLoftSrf(run)
        #for each in srf:
        
        norm = rs.SurfaceNormal(srf[0], [.5,.5])
        if norm.Z < 0:
            rs.FlipSurface(srf[0], True)
            runGeo.append(srf[0])
        else:
            runGeo.append(srf[0])
        
        rs.DeleteObjects(run)
    
    
    landingEdges = []
    for run in runGeo:
        curves = rs.DuplicateEdgeCurves(run)
        highestIndex = None
        highestValue = -999999
        lowestIndex = None
        lowestValue = 999999
        for i, curve in enumerate(curves):
            crvZ = rs.CurveMidPoint(curve)[2]
            if crvZ < lowestValue:
                lowestIndex = i
                lowestValue = crvZ
            if crvZ > highestValue:
                highestIndex = i
                highestValue = crvZ
        lowestEdge = rs.CopyObject(curves[lowestIndex])
        highestEdge = rs.CopyObject(curves[highestIndex])
        landingEdges.append(lowestEdge)
        rs.ReverseCurve(highestEdge)
        landingEdges.append(highestEdge)
        rs.DeleteObjects(curves)
    
    landingGeos = GetRampLandings(landingEdges)
    rs.EnableRedraw(True)
    
    FinalSrf = rs.JoinSurfaces(runGeo + landingGeos, True)
    
    return FinalSrf

def main():
    #path = rs.GetCurveObject("Select ramp path")
    path = rs.GetObject("Select Ramp Path", rs.filter.curve)
    if path is None: return
    height = rs.GetReal("Ramp height", 60)
    if height is None: return
    #length = rs.GetReal("Ramp Length", 180)
    #if length is None: return
    width = rs.GetReal("Ramp width", 42)
    if width is None: return
    slope = rs.GetReal("Ramp slope (e.g. 10% slope is .10)", .20)
    if slope is None: return
    #MakeRamp(path, length, width, height)
    Ramp_HeightSlope(path, width, height, slope)

if __name__ == "__main__":
    main()