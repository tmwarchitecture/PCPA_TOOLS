import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math
import System.Drawing as drawing
from System.Collections.Generic import List

import utils

__author__ = 'Tim Williams'
__version__ = "2.1.0"

###############################################################################
####01
#GetRunsAndLandings
def GetRunsAndLandings(path, width):
    topLandingExtension = 12
    btmLandingExtension = 12
    
    rhobj = rs.coercecurve(path)
    
    #Split at when not tangent
    dom=rhobj.Domain
    cornerParams=[]
    t=dom[0]
    cont=rc.Geometry.Continuity.C1_locus_continuous
    while True:
        result=rhobj.GetNextDiscontinuity(cont,t,dom[1])
        if not result[0]: break
        t=result[1]
        cornerParams.append(t)
    segments = rhobj.Split(cornerParams)

    #Offset both directions
    offsetSegmentsLeft, offsetSegmentsRight = OffsetBothDir(segments, width)

    #Trim intersecting offset segments
    trimmedSegmentsLeft, elbowsLeft, pitPtsLeft = TrimOffsets(offsetSegmentsLeft)
    trimmedSegmentsRight, elbowsRight, pitPtsRight = TrimOffsets(offsetSegmentsRight)

    #Get ovelaping segments
    centerSegments = GetOverlappingSegments(segments, trimmedSegmentsLeft, trimmedSegmentsRight, width)
    
    #Shorten runs for landing extensions
    centerSegments = RemoveExtensions(centerSegments, topLandingExtension, btmLandingExtension)
    
    #Offset both directions AGAIN
    runSegmentsLeft, runSegmentsRight = OffsetBothDir(centerSegments, width)
    
    #Create landings
    landings, landingsLeft, landingsRight = CreateLandings(runSegmentsLeft, elbowsLeft, pitPtsLeft, runSegmentsRight, elbowsRight, pitPtsRight)
    
    return runSegmentsLeft, runSegmentsRight, landings, landingsLeft, landingsRight

#UTILS
def OffsetBothDir(segments, width):
    """
    Offsets a list of segements in both directions.
    """
    normal = rc.Geometry.Vector3d(0,0,1)
    dist = width/2
    tol = rs.UnitAbsoluteTolerance()

    offsetSegmentsLeft = []
    offsetSegmentsRight = []

    #Get offset segments
    for i, segment in enumerate(segments):
        if segment is None: continue
        startVec = segment.TangentAtStart
        startVec.Rotate(math.pi/2, normal)
        startPt = segment.PointAtStart
        offsetPtLeft = startPt.Add(startPt, startVec)

        offsetSegmentsLeft += segment.Offset(offsetPtLeft, normal, dist, tol, 0)
        offsetSegmentsRight += segment.Offset(offsetPtLeft, normal, -dist, tol, 0)

    return [offsetSegmentsLeft, offsetSegmentsRight]

def TrimOffsets(origLines):
    """
    Trim the end off of intersecting curves
    input:
        origLines = Curves
    return:
        Trimmed curves
    """
    tol = rs.UnitAbsoluteTolerance()
    trimmedCurves = []
    elbowCurves = []
    pitPoints = []
    #for each in origLines:
    #    sc.doc.Objects.Add(each)
    
    for i, each in enumerate(origLines):
        if i == 0: #Dont intersect prev segment if first segment
            lowerParam = each.Domain.T0
        else:
            #Intersection with previous segment
            intersections = rc.Geometry.Intersect.Intersection.CurveCurve(origLines[i-1], origLines[i], tol, tol)
            
            if intersections.Count == 0: #No intersection with prev segment
                lowerParam = each.Domain.T0 #So, lowerParam = start of this segment
                #ITS AN ELBOW
                elbowCurves.append(ExtendTangents(origLines[i-1], origLines[i]))
                pitPoints.append(None)
            else:
                lowerParam = intersections.Item[0].ParameterB #There was intersectino with prev segment, so lowerparam = intersection param
                #ITS A PIT
                elbowCurves.append(None)
                pitPoints.append(intersections.Item[0].PointA)

        if i == len(origLines)-1: #Dont intersect next segment if last segment
            higherParam = each.Domain.T1
        else:
            #Intersection with Next segment
            intersections = rc.Geometry.Intersect.Intersection.CurveCurve(origLines[i+1], origLines[i], tol, tol)
            if intersections.Count == 0: #No intersection with prev segment
                higherParam = each.Domain.T1 #So, lowerParam = end of this segment
                #Its an elbow
                elbowCurves.append(ExtendTangents(origLines[i], origLines[i+1], False))
                pitPoints.append(None)
            else:
                higherParam = intersections.Item[0].ParameterB #There was intersectino with prev segment, so lowerparam = intersection param
                #Its a pit
                elbowCurves.append(None)
                pitPoints.append(intersections.Item[0].PointA)

        domain = rc.Geometry.Interval(lowerParam, higherParam)
        trimmedCurves.append(each.Trim(domain))
    return trimmedCurves, elbowCurves, pitPoints

def GetOverlappingSegments(segments, trimmedSegmentsLeft, trimmedSegmentsRight, width):
    centerSegments = []
    for i, segment in enumerate(segments):
        stParamLeft = segment.ClosestPoint(trimmedSegmentsLeft[i].PointAtStart, width)
        stParamRight = segment.ClosestPoint(trimmedSegmentsRight[i].PointAtStart, width)

        endParamLeft = segment.ClosestPoint(trimmedSegmentsLeft[i].PointAtEnd, width)
        endParamRight = segment.ClosestPoint(trimmedSegmentsRight[i].PointAtEnd, width)

        domain = rc.Geometry.Interval(max([stParamLeft[1], stParamRight[1]]), min([endParamLeft[1], endParamRight[1]]))
        if domain[0] >= domain[1]:
            print "A segment was trimmed out of existence"
        centerSegments.append(segment.Trim(domain))
    return centerSegments

def RemoveExtensions(centerSegments, topLandingExtension = 0, btmLandingExtension = 0):
    for i, centerSegment in enumerate(centerSegments):
        length = centerSegment.GetLength()
        if length > topLandingExtension+btmLandingExtension:
            if i == 0:
                btmParam = 0
            else: 
                btmParam = centerSegment.LengthParameter(btmLandingExtension)[1]
            if i == len(centerSegments)-1:
                topParam = centerSegment.ClosestPoint(centerSegment.PointAtEnd)[1]
            else:
                topParam = centerSegment.LengthParameter(length-topLandingExtension)[1]
            dom = rc.Geometry.Interval(btmParam, topParam)
            centerSegments[i] = centerSegment.Trim(dom)
    return centerSegments

def CreateLandings(segmentsLeft, elbowsLeft, pitsLeft, segmentsRight, elbowsRight, pitsRight):
    """
    returns:
        polyline (list): Closed planar landing curves
    """
    allLandings = []
    leftLandings = []
    rightLandings = []
    for i in range(0,len(segmentsLeft)-1):
        #CONSTRUCT LANDING
        pt0 = segmentsLeft[i].PointAtEnd
        pt1 = segmentsRight[i].PointAtEnd
        pt2 = segmentsRight[i+1].PointAtStart
        pt3 = segmentsLeft[i+1].PointAtStart
        if pitsLeft[i*2] is None: #Its turning right
            ptA = pitsRight[i*2]
            ptB = elbowsLeft[i*2].PointAt(1)
        else:
            ptB = pitsLeft[i*2]
            ptA = elbowsRight[i*2].PointAt(1)
        
        pts = []
        ptsLeft = []
        ptsRight = []
        
        pts.append(pt0)
        pts.append(pt1)
        ptsRight.append(pt1)
        if rs.Distance(pt1, ptA) > rs.UnitAbsoluteTolerance():
            pts.append(ptA)
            ptsRight.append(ptA)
        if rs.Distance(pts[-1], pt2) <= rs.UnitAbsoluteTolerance():
            del pts[-1]
            del ptsRight[-1]
        pts.append(pt2)
        ptsRight.append(pt2)
        pts.append(pt3)
        ptsLeft.append(pt3)
        if rs.Distance(pt3, ptB) > rs.UnitAbsoluteTolerance():
            pts.append(ptB)
            ptsLeft.append(ptB)
        if rs.Distance(pts[-1], pt0) > rs.UnitAbsoluteTolerance():
            pts.append(pt0)
            ptsLeft.append(pt0)
        
        allLandings.append(rc.Geometry.PolylineCurve(pts))
        
        #LANDING EDGES
        if len(ptsRight) > 1:
            rightLandings.append(rc.Geometry.PolylineCurve(ptsRight))
        else:
            rightLandings.append(None)
        if len(ptsLeft) > 1:
            leftLandings.append(rc.Geometry.PolylineCurve(ptsLeft))
        else:
            leftLandings.append(None)
    return allLandings, leftLandings, rightLandings

def ExtendTangents(segment1, segment2, dir = True):
    """
    dir = True: For previous segment
    """
    #dir = True
    tol = rs.UnitAbsoluteTolerance()

    #if dir:
    seg1EndPt = segment1.PointAtEnd
    line1EndPt = seg1EndPt.Add(seg1EndPt, segment1.TangentAtEnd)
    line1 = rc.Geometry.Line(seg1EndPt, line1EndPt)

    seg2StPt = segment2.PointAtStart
    line2EndPt = seg2StPt.Add(seg2StPt, -segment2.TangentAtStart)
    line2 = rc.Geometry.Line(seg2StPt, line2EndPt)

    #sc.doc.Objects.AddLine(line1)
    #sc.doc.Objects.AddLine(line2)

    intersections = rc.Geometry.Intersect.Intersection.LineLine(line1, line2, tol, False)
    testLen1 = intersections[1]
    testLen2 = intersections[2]

    if dir:
        newEndPt = line1.PointAtLength(intersections[1])
        finalLine = rc.Geometry.Line(seg1EndPt, newEndPt)
    else:
        newEndPt = line2.PointAtLength(intersections[1])
        finalLine = rc.Geometry.Line(seg2StPt, newEndPt)

    #sc.doc.Objects.AddLine(finalLine)
    return finalLine

##############################################################################
####01-B
def CreateOutlines(leftSegments, rightSegments, landingsLeft, landingsRight):
    startLine = rc.Geometry.LineCurve(leftSegments[0].PointAtStart, rightSegments[0].PointAtStart)
    endLine = rc.Geometry.LineCurve(leftSegments[-1].PointAtEnd, rightSegments[-1].PointAtEnd)
    
    leftCrvs = []
    rightCrvs = []
    
    for each in leftSegments:
        if each is not None:
            leftCrvs.append(each)
    for each in landingsLeft:
        if each is not None:
            leftCrvs.append(each)
    
    for each in rightSegments:
        if each is not None:
            rightCrvs.append(each)
    for each in landingsRight:
        if each is not None:
            rightCrvs.append(each)
    
    #allCrvs.append(startLine)
    #allCrvs.append(endLine)
    
    #edges = rc.Geometry.Curve.JoinCurves(allCrvs)[0]
    leftEdges = rc.Geometry.Curve.JoinCurves(leftCrvs)[0]
    rightEdges = rc.Geometry.Curve.JoinCurves(rightCrvs)[0]
    #sc.doc.Objects.Add(x)
    return leftEdges, rightEdges

###############################################################################
####02
#CALCULATE AND MAKE 2D TREADS
def Make2DTreads(obj, leftSegments, rightSegments, width, height):
    if rs.UnitSystem() == 8:
        minTreadDepth = 11
        maxTreadDepth = 0
        minRiserHeight = 4
        maxRiserHeight = 7
        numExtraTreads = 2
        extraTreadLength = 12
    else:
        print "Only inches supported"
        return None

    #Change from left and right lists to short and long
    shortEdges = []
    longEdges = []
    for i in range(len(leftSegments)):
        if leftSegments[i].GetLength() > rightSegments[i].GetLength():
            shortEdges.append(rightSegments[i])
            longEdges.append(leftSegments[i])
        else:
            shortEdges.append(leftSegments[i])
            longEdges.append(rightSegments[i])

    #Check global
    numRisersFromHeight = int(math.floor((height/maxRiserHeight)))
    totalLength = 0
    for i in range(len(shortEdges)):
        length = shortEdges[i].GetLength()
        #sc.doc.Objects.Add(shortEdges[i])
        totalLength += (length - extraTreadLength)
        print

    maxNumRisers = int(math.floor(totalLength/minTreadDepth))
    minNumRisers = int(math.floor(height/maxRiserHeight))

    if numRisersFromHeight > maxNumRisers :
        print "Path not long enough to reach full height"
    if numRisersFromHeight < minNumRisers:
        print "Not enough risers to reach full height"

    #Get num risers
    numRisers = []
    for i in range(len(shortEdges)):
        length = shortEdges[i].GetLength()
        usableLength = length - extraTreadLength

        percentOfLength = usableLength / totalLength
        x = round(percentOfLength*numRisersFromHeight)
        numRisers.append(x)

    #Draw riser lines
    allRiserLines = []
    treadLengths = []
    for i in range(len(shortEdges)):
        length = shortEdges[i].GetLength()
        numTreads = numRisers[i]

        if numTreads == 0:
            continue

        riserStParams = shortEdges[i].DivideByCount(numTreads, True)
        treadLengths.append(length/numTreads)
        riserLines = []
        for riserStParam in riserStParams:
            shortEdgePt = shortEdges[i].PointAt(riserStParam)
            result = IsPointOnLeftSide(shortEdgePt, obj)
            longEdgeParam = longEdges[i].ClosestPoint(shortEdges[i].PointAt(riserStParam), width*2)[1]
            longEdgePt = longEdges[i].PointAt(longEdgeParam)
            line = rc.Geometry.LineCurve(shortEdgePt, longEdgePt)
            if result:
                line.Reverse()
            riserLines.append(line)
        allRiserLines.append(riserLines)

    return allRiserLines, numRisers, treadLengths

def IsPointOnLeftSide(point, curve):
    rhcrv = rs.coercecurve(curve)
    closestPtParam = rhcrv.ClosestPoint(point)[1]
    closestPt = rhcrv.PointAt(closestPtParam)
    vec = rs.VectorCreate(closestPt, point)
    tanVec = rhcrv.TangentAt(closestPtParam)
    x = tanVec.VectorAngle(tanVec, vec, rs.WorldXYPlane())
    if math.degrees(x)-180 > 0:
        return False
    else:
        return True

###############################################################################
####03
#MAKE 2D SRFS
def MakeTreadSurfaces(leftSegments, rightSegments, landings, allTreads, preview = True):
    tol = rs.UnitAbsoluteTolerance()

    #Make tread surfaces
    treadSrfs = []
    for i, each in enumerate(leftSegments):
        edge1 = allTreads[i][0]
        edge2 = allTreads[i][-1]
        edge3 = each
        edge4 = rightSegments[i]
        boundary = rc.Geometry.Curve.JoinCurves([edge1, edge3, edge2, edge4])[0]
        if boundary.ClosedCurveOrientation() == rc.Geometry.CurveOrientation.Clockwise:
            boundary.Reverse()
        planarSrf = rc.Geometry.Brep.CreatePlanarBreps(boundary, tol)[0]
        treadSrf = planarSrf.Faces[0].Split(allTreads[i], tol)
        treadSrfs.append(treadSrf)
        if preview:
            sc.doc.Objects.AddBrep(treadSrf)

    #Create Landing Surfaces
    landingSrfs = []
    for each in landings:
        
        planarSrf = rc.Geometry.Brep.CreatePlanarBreps([each], tol)[0]
        landingSrfs.append(planarSrf)
        if preview:
            sc.doc.Objects.AddBrep(planarSrf)
    return treadSrfs, landingSrfs

###############################################################################
####04
#3D GEO
def ConstructRiserSrfs(allTreads, landingSrfs, riserHeight):
    currRiserHeight = 0
    riserSrfs = []
    for eachRunsTreads in allTreads:
        #thisRunsRisers = []
        for eachLine in eachRunsTreads:
            stPt = eachLine.PointAtStart
            #ADD TEST TO SEE IF POINT ON LEFT OR RIGHT SIDE OF CURVE, THEN FLIP
            eachLine.Translate(0,0,currRiserHeight)
            endPt = rc.Geometry.Point3d.Add(stPt, rc.Geometry.Vector3d(0,0,riserHeight))
            line = rc.Geometry.LineCurve(stPt, endPt)
            sumSrf = rc.Geometry.SumSurface.Create(eachLine, line)
            brep = sumSrf.ToBrep()
            riserSrfs.append(brep)
            
            currRiserHeight += riserHeight
        #riserSrfs.append(thisRunsRisers)
    del riserSrfs[-1]
    #for eachRunsTreads in riserSrfs:
    #    sc.doc.Objects.Add(eachRunsTreads)
    
    print
    return riserSrfs

def ConstructTreadSrfs(obj, treadSrfs, landingSrfs, riserHeight):
    rhobj = rs.coercecurve(obj)
    currRiserHeight = riserHeight
    
    #CONSTRUCT BREPS
    finalTreadSrfs = []
    
    landingHeights = []
    
    for i, eachRun in enumerate(treadSrfs):
        #EACH RUN
        treads = []
        params = []
        for eachFace in eachRun.Faces:
            brep = eachFace.DuplicateFace(False)
            treads.append(brep)
            bbox = brep.GetBoundingBox(True)
            params.append(rhobj.ClosestPoint(bbox.Center)[1])
        
        #SORT
        yx = zip(params, treads)
        yx.sort()
        treads = [x for y, x in yx]
        
        #MOVE FACES
        for eachFace in treads:
            eachFace.Translate(0,0,currRiserHeight)
            currRiserHeight += riserHeight
            #sc.doc.Objects.Add(eachFace)
            finalTreadSrfs.append(eachFace)
        
        #DO THE LANDING
        if i < len(landingSrfs):
            landingSrfs[i].Translate(0,0,currRiserHeight)
            landingHeights.append(currRiserHeight)
            #sc.doc.Objects.Add(landingSrfs[i]) 
            currRiserHeight += riserHeight
            finalTreadSrfs.append(landingSrfs[i])
    
    return finalTreadSrfs, landingHeights

def CreateUnderSurfaces(treadSrfs, leftSegments, rightSegments, allTreads, riserHeight):
    extensionFactor = 1.1
    extensionLength = 6
    currRiserHeight = riserHeight
    underSrfs = []
    
    for i in range(len(leftSegments)):
        leftSegment = leftSegments[i]
        rightSegment = rightSegments[i]
        treads = allTreads[i]

        treadList = List[rc.Geometry.Curve]()
        for j, eachTread in enumerate(treads):
            #moveVec = rc.Geometry.Vector3d(0,0,currRiserHeight)
            #eachTread.Translate(moveVec)
            xCrv = eachTread.Extend(rc.Geometry.CurveEnd.Both, extensionLength, rc.Geometry.CurveExtensionStyle.Smooth)
            treadList.Add(xCrv)
            currRiserHeight += riserHeight
            #sc.doc.Objects.Add(xCrv)

        srf = rc.Geometry.Brep.CreateFromLoft(treadList, rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
        #sc.doc.Objects.Add(srf)
        underSrfs.append(srf)
        #print
    return underSrfs

def CreateSides(leftEdge, rightEdge, height):
    stPtLeft = leftEdge.PointAtStart
    stPtRight = rightEdge.PointAtStart
    vec = rc.Geometry.Vector3d(0,0,height)
    
    line = rc.Geometry.LineCurve(stPtLeft, rc.Geometry.Point3d.Add(stPtLeft, vec))
    leftEdge.Reverse()
    geoLeft = rc.Geometry.SumSurface.Create(leftEdge, line)
    geoRight = rc.Geometry.SumSurface.Create(rightEdge, line)
    
    return geoLeft.ToBrep(), geoRight.ToBrep()

def CreateUnderWedge(landings, landingsLeft, landingsRight, landingSrfs, landingHeights, riserHeight, treadLengths, thickness):
    wedges = []
    for i, landingLeft in enumerate(landingsLeft):
        rightStartPt = landingsRight[i].PointAtStart
        rightVec = landingsRight[i].TangentAtStart
        leftStartPt = landingsLeft[i].PointAtEnd
        leftVec = landingsLeft[i].TangentAtEnd
        leftVec.Reverse()
        
        riseRatio = riserHeight/treadLengths[i]
        rightVec.Z = riseRatio
        leftVec.Z = riseRatio
        factor = riserHeight/riseRatio
        
        directionEndPtRight = rc.Geometry.Point3d.Add(rightStartPt, rightVec*factor)
        directionEndPtLeft = rc.Geometry.Point3d.Add(leftStartPt, leftVec*factor)
        
        diagonalRight = rc.Geometry.LineCurve(rightStartPt, directionEndPtRight)
        diagonalLeft = rc.Geometry.LineCurve(leftStartPt, directionEndPtLeft)
        
        directionEndPtRight.Z = rightStartPt.Z
        directionEndPtLeft.Z = rightStartPt.Z
        
        horizLineRight = rc.Geometry.LineCurve(rightStartPt, directionEndPtRight)
        horizLineLeft = rc.Geometry.LineCurve(leftStartPt, directionEndPtLeft)
        horizLineLeft.Reverse()
        
        #VERTICAL LINE
        riseVec = rc.Geometry.Vector3d(0,0,riserHeight)
        topPt = rc.Geometry.Point3d.Add(rightStartPt, riseVec)
        secLine = rc.Geometry.LineCurve(rightStartPt, leftStartPt)
        vertLine = rc.Geometry.LineCurve(rightStartPt, topPt)
        
        treadList = [diagonalRight, diagonalLeft]
        
        underSrf = rc.Geometry.Brep.CreateFromLoft(treadList, rc.Geometry.Point3d.Unset, rc.Geometry.Point3d.Unset, rc.Geometry.LoftType.Normal, False)[0]
        rightSrf = rc.Geometry.SumSurface.Create(horizLineRight, vertLine)
        rightBrep = rightSrf.ToBrep()
        leftSrf = rc.Geometry.SumSurface.Create(horizLineLeft, vertLine)
        leftBrep = leftSrf.ToBrep()
        
        rightTriangles = rightBrep.Trim(underSrf, rs.UnitAbsoluteTolerance())
        leftTriangles = leftBrep.Trim(underSrf, rs.UnitAbsoluteTolerance())
        print
        geoList = List[rc.Geometry.Brep]()
        geoList.Add(underSrf)
        for rightTriangle in rightTriangles:
            geoList.Add(rightTriangle)
        for leftTriangle in leftTriangles:
            geoList.Add(leftTriangle)
        brep = rc.Geometry.Brep.JoinBreps(geoList, rs.UnitAbsoluteTolerance())[0]
        brep.Translate(rc.Geometry.Vector3d(0,0,landingHeights[i]-riserHeight-thickness))
        underSrf.Translate(rc.Geometry.Vector3d(0,0,landingHeights[i]-riserHeight-thickness))
        
        
        
        brep.Flip()
        
        dupSrf = landingSrfs[i].Duplicate()
        dupSrf.Translate(rc.Geometry.Vector3d(0,0,-thickness))
        newSrfs = dupSrf.Trim(brep, rs.UnitAbsoluteTolerance())
        for newSrf in newSrfs:
            newSrf.Flip()
            underSrf.Join(newSrf, rs.UnitAbsoluteTolerance(), True)
            #sc.doc.Objects.Add(newSrf)
        
        sc.doc.Objects.Add(underSrf)
        wedges.append(brep)
    return wedges

###############################################################################
####05
#TRIM AND JOIN
def JoinTopSrfs(riserSrfs, treadSrfs, leftSide, rightSide):
    allGeo = riserSrfs + treadSrfs
    brep = rc.Geometry.Brep.JoinBreps(allGeo , rs.UnitAbsoluteTolerance())
    sc.doc.Objects.AddBrep(brep[0])
    
    rightSideTrimmed0 = rightSide.Trim(brep[0], rs.UnitAbsoluteTolerance())
    leftSideTrimmed0 = leftSide.Trim(brep[0], rs.UnitAbsoluteTolerance())
    sc.doc.Objects.Add(rightSideTrimmed0[0])
    sc.doc.Objects.Add(leftSideTrimmed0[0])
    
    print

def TrimUnderSrfsWithSides(underSrfs, leftSide, rightSide, thickness):
    for eachUnderSrf in underSrfs:
        srf1 = eachUnderSrf.Trim(rightSide , rs.UnitAbsoluteTolerance())[0]
        srf2 = srf1.Trim(leftSide , rs.UnitAbsoluteTolerance())
        finalSrf = srf2[0]
        
        finalSrf.Translate(rc.Geometry.Vector3d(0,0,-thickness))
        
        sc.doc.Objects.Add(finalSrf)

    
    print

###############################################################################
###############################################################################
###############################################################################
#MAIN FUNCTION
def MakeStair(obj, width, height):
    ####00
    #VARIABLES
    structThickness = 9
    
    ####01
    #Get the 2d run and landings
    leftSegments, rightSegments, landings, landingsLeft, landingsRight  = GetRunsAndLandings(obj, width)

    ####01-B
    #MAKE OUTLINE
    leftEdge, rightEdge = CreateOutlines(leftSegments, rightSegments, landingsLeft, landingsRight)

    #Temp preview
    if False:
        for each in leftSegments:
            sc.doc.Objects.Add(each)
        for each in rightSegments:
            sc.doc.Objects.Add(each)
        for each in landings:
            sc.doc.Objects.Add(each)


    ####02
    #Draw 2d treads
    allTreads, numRisers, treadLengths = Make2DTreads(obj, leftSegments, rightSegments, width, height)
    if allTreads is None: return
    #Temp Preview
    if False:
        for each in allTreads:
            for eachLine in each:
                sc.doc.Objects.Add(eachLine)


    ####03
    #Make Tread Surfaces
    treadSrfs, landingSrfs = MakeTreadSurfaces(leftSegments, rightSegments, landings, allTreads, False)

    #RISER HEIGHT
    riserHeight = height/(sum(numRisers) + len(landingSrfs)+1)


    ####04
    #MAKE RISER SURFACES
    riserSrfs = ConstructRiserSrfs(allTreads, landingSrfs, riserHeight)

    #MAKE TREAD SURFACES
    treadSrfs, landingHeights = ConstructTreadSrfs(obj, treadSrfs, landingSrfs, riserHeight)

    #Make UnderSurface
    underSrfs = CreateUnderSurfaces(treadSrfs, leftSegments, rightSegments, allTreads, riserHeight)

    #CREATE SIDES
    leftSide, rightSide = CreateSides(leftEdge, rightEdge, height)
    
    #Create Underwedge
    wedges = CreateUnderWedge(landings, landingsLeft, landingsRight, landingSrfs, landingHeights, riserHeight, treadLengths, structThickness)

    ####05
    #JOIN TOP SRFS
    JoinTopSrfs(riserSrfs, treadSrfs, leftSide, rightSide)
    TrimUnderSrfsWithSides(underSrfs, leftSide, rightSide, structThickness)
    
###############################################################################
#RHINO BUTTON INTERFACE
def MakeStair_Button():
    tol = rs.UnitAbsoluteTolerance()
    objs = rs.GetObjects("Select guide path")
    if objs is None: return

    height = rs.GetReal("Stair Height", number = 120)
    if height is None: return

    width = rs.GetReal("Stair Width", number = 30)
    if width is None: return

    for obj in objs:
        MakeStair(obj, width, height)

if __name__ == "__main__":
    MakeStair_Button()
