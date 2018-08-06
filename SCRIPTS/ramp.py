import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import utils
import layers

__author__ = 'Tim Williams'
__version__ = "2.0.0"

def MakeRampRuns(path, width):
    topOffset = 12
    btmOffset = 12
    newPath = rs.CopyObject(path)
    segments = rs.ExplodeCurves(newPath, True)
    if len(segments) < 1:
        segments = [newPath]


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
    handrailLines = []

    #Entering Loop For each segment
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

            if i != 0:
                longVec = rs.VectorReverse(rs.VectorCreate(widthStPt, nextSegOffsetStPt))
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), btmOffset)
                stLine = rs.MoveObject(stLine, longVec)
            if i != len(segments)-1:
                longVec = rs.VectorCreate(widthStPt, nextSegOffsetStPt)
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), topOffset)
                endLine = rs.MoveObject(endLine, longVec)
        else:
            stLine = rs.AddLine(widthEndPt, widthStPt)
            shortVec = rs.VectorCreate(widthStPt, widthEndPt)
            pt4 = rs.CopyObject(nextSegOffsetStPt, shortVec)
            endLine = rs.AddLine(nextSegOffsetStPt, pt4)

            if i != 0:
                longVec = rs.VectorReverse(rs.VectorCreate(widthEndPt, nextSegOffsetStPt))
                longVec = rs.VectorScale(rs.VectorUnitize(longVec), btmOffset)
                stLine = rs.MoveObject(stLine, longVec)
            if i != len(segments)-1:
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

def MakeRampLandings(allLines, hdrlCtrOffset):
    landingGeo = []
    hdrls = []
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
        try:
            stInter = rs.AddPoint(rs.LineLineIntersection(stLineBtm, stLine)[0])
        except:
            stInter = stPt
        try:
            endInter = rs.AddPoint(rs.LineLineIntersection(endLineBtm, endLine)[0])
        except:
            endInter = endPt

        landingPts = [stPt, endPt, endInter, endPtBtm, stPtBtm, stInter, stPt]
        landingCrv = rs.AddPolyline(landingPts)
        landingGeo.append(rs.AddPlanarSrf(landingCrv))

        #Handrails
        hdrl1 = rs.AddPolyline([stPt, stInter, stPtBtm])
        hdrl1b = rs.OffsetCurve(hdrl1 , endPt, hdrlCtrOffset, (0,0,1))
        hdrls.append(hdrl1b)
        hdrl2 = rs.AddPolyline([endPt, endInter, endPtBtm])
        hdrl2b = rs.OffsetCurve(hdrl2, stPt, hdrlCtrOffset, (0,0,1))
        hdrls.append(hdrl2b)

        rs.DeleteObject(hdrl1)
        rs.DeleteObject(hdrl2)

        rs.DeleteObject(landingCrv)
        rs.DeleteObject(stLine)
        rs.DeleteObject(endLine)
        rs.DeleteObject(stLineBtm)
        rs.DeleteObject(endLineBtm)
        try:
            rs.DeleteObjects([stPtOffset, endPtOffset, stPtOffsetBtm, endPtOffsetBtm, stInter, endInter])
        except:
            rs.DeleteObjects([stPtOffset, endPtOffset, stPtOffsetBtm, endPtOffsetBtm])
    rs.DeleteObjects(allLines)
    return landingGeo, hdrls

def MakeHandrailFromRuns(run, HDRLoffset):
    pt1 = rs.CurveStartPoint(run[0])
    pt2 = rs.CurveStartPoint(run[1])

    pt3 = rs.CurveEndPoint(run[0])
    pt4 = rs.CurveEndPoint(run[1])

    crossVec = rs.VectorCreate(pt3, pt1)
    crossVec = rs.VectorUnitize(crossVec)
    crossVec = rs.VectorScale(crossVec, HDRLoffset)

    edge1 = rs.AddLine(pt1, pt2)
    edge2 = rs.AddLine(pt3, pt4)
    edge1 = rs.MoveObject(edge1,crossVec)
    edge2 = rs.MoveObject(edge2, rs.VectorReverse(crossVec))

    return [edge1, edge2]

def CheckRunLengths(runs):
    lengthComment = ''
    for i, run in enumerate(runs):
        dist = rs.Distance(rs.CurveStartPoint(run[0]), rs.CurveStartPoint(run[1]))
        if dist > 360:
            lengthComment += 'Run {} requires a landing\n'.format(i+1)
            templine = rs.AddLine(rs.CurveStartPoint(run[0]), rs.CurveStartPoint(run[1]))
            mdPt = rs.CurveMidPoint(templine)
            vec = rs.VectorCreate(mdPt, rs.CurveStartPoint(run[0]))
            landingCenter = rs.CopyObject(run[0], vec)
            vec = rs.VectorScale(rs.VectorUnitize(vec), 30)
            upperLine = rs.CopyObject(landingCenter, vec)
            vec = rs.VectorReverse(vec)
            lowerLine = rs.MoveObject(landingCenter, vec)
            rs.DeleteObject(templine)
            run.insert(1, lowerLine)
            run.insert(2, upperLine)

    flatList = []
    for item in runs:
        for each in item:
            flatList.append(each)

    pairs = []
    for i in range(0, len(flatList), 2):
        pairs.append([flatList[i], flatList[i+1]])
    return pairs, lengthComment

def Ramp_HeightSlope(path, width, slope):
    #Variables
    rampThickness = 6
    handrailOffset = 3
    handrailRadius = 1.5
    handrailHeight = 34
    if width < 36:
        width = 36
    width = width + (handrailOffset*2)
    comments = ''

    handrailCenterlineOffset = (handrailOffset - handrailRadius/2)

    rs.SimplifyCurve(path)

    runs = MakeRampRuns(path, width)

    if slope > .05:
        runData = CheckRunLengths(runs)
        runs = runData[0]
        comments += runData[1]

    runGeo = []
    hdrls = []
    finalHandrails = []
    vertMove = (0,0,0)

    for run in runs:
        length = rs.Distance(rs.CurveStartPoint(run[0]), rs.CurveStartPoint(run[1]))

        stHeight = vertMove
        vertMove = (0,0,length * slope)

        rs.MoveObject(run[-1], vertMove)
        rs.MoveObjects(run, stHeight)

        vertMove = rs.VectorAdd(stHeight, vertMove)

        srf = rs.AddLoftSrf(run)

        norm = rs.SurfaceNormal(srf[0], [.5,.5])
        if norm.Z < 0:
            rs.FlipSurface(srf[0], True)
            runGeo.append(srf[0])
        else:
            runGeo.append(srf[0])

        hdrls.append(MakeHandrailFromRuns(run, handrailCenterlineOffset))

        rs.DeleteObjects(run)

    #Get highest and lowest lines
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
    comments += 'Total ramp height {}"\n'.format(str(highestValue))

    #Make Landings
    landingGeos = MakeRampLandings(landingEdges, handrailCenterlineOffset)
    landings = landingGeos[0]
    hdrls += landingGeos[1]
    allHandrails = []
    for hdrl in hdrls:
        for each in hdrl:
            allHandrails.append(each)
    longRails = rs.JoinCurves(allHandrails, True)


    #Handrail Extension
    for rail in longRails:
        stPt = rs.CurveStartPoint(rail)
        stVec = rs.CurveTangent(rail, 0)
        stVecProj = rs.VectorScale(rs.VectorReverse(rs.VectorUnitize((stVec[0], stVec[1], 0))), 12)
        endPt = rs.CurveEndPoint(rail)
        endParam = rs.CurveClosestPoint(rail, endPt)
        endVec = rs.CurveTangent(rail, endParam)
        endVecProj = rs.VectorScale(rs.VectorUnitize((endVec[0], endVec[1], 0)), 12)
        stPtTemp = rs.CurveStartPoint(rail)
        endPtTemp = rs.CurveEndPoint(rail)
        stPtOffset = rs.MoveObject(stPtTemp , stVecProj)
        endPtOffset = rs.MoveObject(endPtTemp , endVecProj)
        stProj = rs.AddLine(stPt, stPtOffset)
        endProj = rs.AddLine(endPt, endPtOffset)
        finalHandrails.append(rs.JoinCurves([stProj, rail, endProj], True)[0])

        rs.DeleteObject(stPtOffset)
        rs.DeleteObject(endPtOffset)

    #Move handrails up
    for rail in finalHandrails:
        rs.MoveObject(rail, (0,0,handrailHeight))

    #Make solid geometry
    topSurface = rs.JoinSurfaces(runGeo + landings, True)
    if topSurface is None: topSurface = runGeo

    btmSurface = rs.CopyObject(topSurface, (0,0,-rampThickness))

    edgeCurves = rs.DuplicateSurfaceBorder(topSurface)

    extrusionLine = rs.AddLine((0,0,0) , (0,0,-rampThickness))
    extrusionGeo = rs.ExtrudeCurve(edgeCurves, extrusionLine)
    rs.DeleteObject(extrusionLine)
    rs.DeleteObject(edgeCurves)

    finalGeo = rs.JoinSurfaces([topSurface, btmSurface, extrusionGeo], True)

    #rs.EnableRedraw(True)
    #print "A"
    if slope <= .05:
        rs.DeleteObjects(finalHandrails)
        return [finalGeo, comments]
    else:
        return [finalGeo, comments, finalHandrails]

def main():
    path = rs.GetObject("Select Ramp Path", rs.filter.curve, True)
    if path is None: return

    if 'ramp-widthDefault' in sc.sticky:
        widthDefault = sc.sticky['ramp-widthDefault']
    else:
        widthDefault = 36
    if 'ramp-slopeDefault' in sc.sticky:
        slopeDefault = sc.sticky['ramp-slopeDefault']
    else:
        slopeDefault = 8.333


    width = rs.GetReal("Ramp Clear Width", widthDefault, minimum = 36)
    if width is None: return
    slope = rs.GetReal("Ramp slope (e.g. 8.33%(1:12) is 8.33)", slopeDefault)
    if slope is None: return

    sc.sticky['ramp-widthDefault'] = width
    sc.sticky['ramp-slopeDefault'] = slope

    rs.EnableRedraw(False)
    rampGeoList = Ramp_HeightSlope(path, width, slope/100)
    try:
        layers.AddLayerByNumber(402, False)
        layerName = layers.GetLayerNameByNumber(402)

        rs.ObjectLayer(rampGeoList[0], layerName)
        try:
            if rampGeoList[2] is not None:
                layers.AddLayerByNumber(106, False)
                layerName = layers.GetLayerNameByNumber(106)

                rs.ObjectLayer(rampGeoList[2], layerName)
        except:
            pass
        result = True
    except:
        result = False

    utils.SaveFunctionData('Architecture-ramp', [width, slope, str([(pt.X, pt.Y, pt.Z) for pt in rs.CurveEditPoints(path)]), result])

    rs.EnableRedraw(True)

    print rampGeoList[1]

    utils.SaveToAnalytics('architecture-ramp')

if __name__ == "__main__":
    main()
