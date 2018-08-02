"""
Makes a stair to specified height.

input: route(pline), width (num), height(num)
returns: 1 Solid Brep
"""

__author__ = 'Tim Williams'
__version__ = '2.0'

import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import math
import utils
import layers


def makeFace(srfs):
    srfsJoined=rs.JoinSurfaces(srfs, True)
    boundaryCrv=rs.DuplicateSurfaceBorder(srfsJoined)
    srf = rs.AddPlanarSrf(boundaryCrv)
    try:
        rs.DeleteObjects(boundaryCrv)
    except:
        pass
    rs.DeleteObject(srfsJoined)
    rs.DeleteObjects(srfs)
    return srf

def getTotalRun(landingEdges):
    run = 0.0
    for i in range(0, len(landingEdges), 2):
        a = rs.CurveMidPoint(landingEdges[i])
        b = rs.CurveMidPoint(landingEdges[i+1])
        run = run + rs.Distance(a, b)
    return run

def mergeCoincidentLines(segments):
    """
    removes coincident, consecutive segments
    
    input: List of GUIDs
    returns: List of GUIDs
    """
    newSegments = []
    i = 0
    while i < len(segments):
        if (i<len(segments)-1): #if coincident, delete both, add new.
            a = rs.VectorCreate(rs.CurveStartPoint(segments[i]), rs.CurveEndPoint(segments[i]))
            b = rs.VectorCreate(rs.CurveStartPoint(segments[i+1]), rs.CurveEndPoint(segments[i+1]))
            a = rs.VectorUnitize(a)
            b = rs.VectorUnitize(b)
            aAng = rs.VectorAngle(a, b)
            if (aAng<.00001):
                newLine = rs.AddLine(rs.CurveStartPoint(segments[i]),rs.CurveEndPoint(segments[i+1]))
                rs.DeleteObject(segments[i])
                rs.DeleteObject(segments[i+1])
                newSegments.append(newLine)
                i = i+2
            else:
                newSegments.append(segments[i]) #if not coincident, add to array
                i = i+1
        else:
            newSegments.append(segments[i]) #add last seg to array
            i = i+1
    return newSegments

def offsetLine(line, dist):
    norm = rs.VectorRotate(rs.CurveTangent(line, rs.CurveParameter(line,0)), 90, [0,0,1])
    norm = rs.VectorScale(rs.VectorUnitize(norm),dist)
    sideStPt = rs.VectorAdd(rs.CurveStartPoint(line),norm)
    sideEndPt = rs.VectorAdd(rs.CurveEndPoint(line),norm)
    newLine = rs.AddLine(sideStPt, sideEndPt)
    return newLine

def rampIntersection(route1, route2, width):
    edges = []
    offSeg1 = offsetLine(route1, width/2)
    offSeg2 = offsetLine(route2, width/2)
    test1 = rs.CurveCurveIntersection(offSeg1, offSeg2)
    if (test1==None):
        side1 = False
    else:   
        side1 = True
    offSeg3 = offsetLine(route1, -width/2)
    offSeg4 = offsetLine(route2, -width/2)
    test2 = rs.CurveCurveIntersection(offSeg3, offSeg4)
    if (test2==None):
        side2 = False
    else:
        side2 = True
    if (side1):
        pivotPt = rs.LineLineIntersection(offSeg1, offSeg2)[0]
        perpPt1 = rs.EvaluateCurve(offSeg3,rs.CurveClosestPoint(offSeg3, pivotPt))
        perpPt2 = rs.EvaluateCurve(offSeg4,rs.CurveClosestPoint(offSeg4, pivotPt))
        edges.append(rs.AddLine(pivotPt, perpPt1))
        edges.append(rs.AddLine(pivotPt, perpPt2))
        elbowPt = rs.LineLineIntersection(offSeg3, offSeg4)[0]
    else:
        pivotPt = rs.LineLineIntersection(offSeg3, offSeg4)[0]
        perpPt1 = rs.EvaluateCurve(offSeg1,rs.CurveClosestPoint(offSeg1, pivotPt))
        perpPt2 = rs.EvaluateCurve(offSeg2,rs.CurveClosestPoint(offSeg2, pivotPt))
        edges.append(rs.AddLine(pivotPt, perpPt1))
        edges.append(rs.AddLine(pivotPt, perpPt2))
        elbowPt = rs.LineLineIntersection(offSeg1, offSeg2)[0]
    rs.DeleteObject(offSeg1)
    rs.DeleteObject(offSeg2)
    rs.DeleteObject(offSeg3)
    rs.DeleteObject(offSeg4)
    landing = rs.AddPolyline([pivotPt, perpPt1, elbowPt, perpPt2, pivotPt])
    return edges, landing

def stairHeight(route, width = 48, height = 120):
    """
    Makes a stair to specified height.
    
    input: route(pline), width (num), height(num)
    returns: Geo
    """
    try:
        rs.EnableRedraw(False)
        rs.SimplifyCurve(route)
        
        if route is None: 
            print("ERROR: No path selected")
            return
        
        if (rs.UnitSystem()==2): #if mm
            maxRiserHeight = 180
            thickness = 200
        if (rs.UnitSystem()==4): #if m
            maxRiserHeight = .180
            thickness = .200
        if (rs.UnitSystem()==8): #if in"
            maxRiserHeight = 7
            thickness = 9
        
        negativeBoo = False
        if (height<0): 
            #if the stair 
            negativeBoo = True
        landingEdges = []
        landings = []
        segments = rs.ExplodeCurves(route)
        if len(segments) < 1:
            segments = [rs.CopyObject(route)]
        landingHeight = []
        geometry = []
        
        #Check that all segments are lines
        for i in range(0, len(segments)):
            if not (rs.IsLine(segments[i])):
                print("ERROR: This function only accepts lines. No arcs or nurb curves.")
                rs.DeleteObjects(segments)
                return
        
        #first landing edge
        norm = rs.VectorRotate(rs.CurveTangent(segments[0], 0), 90, [0,0,1])
        norm = rs.VectorScale(rs.VectorUnitize(norm),width/2)
        side1Pt = rs.VectorAdd(rs.CurveStartPoint(segments[0]),norm)
        side2Pt = rs.VectorAdd(rs.CurveStartPoint(segments[0]),-norm)
        landingEdges.append(rs.AddLine(side1Pt, side2Pt))
        
        #middle landing edges
        for i in range(0, len(segments)-1):
            edgeList, landing = rampIntersection(segments[i],segments[i+1], width)
            landingEdges.append(edgeList[0])
            landingEdges.append(edgeList[1])
            landings.append(landing)
        
        #last landing edge
        norm = rs.VectorRotate(rs.CurveTangent(segments[-1], rs.CurveParameter(segments[-1],1)), 90, [0,0,1])
        norm = rs.VectorScale(rs.VectorUnitize(norm),width/2)
        side1Pt = rs.VectorAdd(rs.CurveEndPoint(segments[-1]),norm)
        side2Pt = rs.VectorAdd(rs.CurveEndPoint(segments[-1]),-norm)
        landingEdges.append(rs.AddLine(side1Pt, side2Pt))
        
        #Add risers
        riserCrvs = []
        treadVecs = []
        numRisersPerRun = []
        numRisers = abs(int(math.ceil(height/maxRiserHeight)))
        risersSoFar = 0
        totalRun = getTotalRun(landingEdges)
        optTreadDepth = totalRun/(numRisers-1) 
        #2R+T = 635
        riserHeight = height/numRisers
        if (negativeBoo):
            curRiserHeight = 0
        else:
            curRiserHeight = riserHeight
        for i in range(0, len(landingEdges), 2): #find numRisers in each run
            a = rs.CurveMidPoint(landingEdges[i])
            b = rs.CurveMidPoint(landingEdges[i+1])
            runDist = rs.Distance(a, b)
            numRisersThisRun = int(round((runDist/optTreadDepth),0))
            if (numRisersThisRun==0):
                numRisersThisRun = 1
            if (i==len(landingEdges)-2): #if last run, add the rest of the risers
                numRisersThisRun = numRisers-risersSoFar
            else:
                risersSoFar = risersSoFar + numRisersThisRun
            numRisersPerRun.append(numRisersThisRun)
        
        #Create Risers on Plan
        for i in range(0, len(landingEdges), 2):
            run = []
            a = rs.CurveMidPoint(landingEdges[i])
            b = rs.CurveMidPoint(landingEdges[i+1])
            centerStringer = rs.AddLine(a, b)
            runDist = rs.Distance(a, b)
            numRisersThisRun = numRisersPerRun[int(i/2)] #risers in this run
            tarPts = rs.DivideCurve(centerStringer, numRisersThisRun, create_points = False)
            rs.DeleteObject(centerStringer)
            for j in range(0, numRisersThisRun+1):
                if (j==0):
                    treadVecs.append(rs.VectorCreate(tarPts[0], tarPts[1]))
                transVec = rs.VectorCreate(tarPts[0], tarPts[j])
                run.append(rs.CopyObject(landingEdges[i], -transVec))
            riserCrvs.append(run)
            print('Flight {0} has {1} risers: {3}" tall, Treads: {2}" deep'.format(int(i/2)+1, numRisersThisRun, rs.VectorLength(treadVecs[int(i/2)]), riserHeight))
        #Move riser edges vertically
        for i in range(0, len(riserCrvs)):
            triangles = []
            if (negativeBoo):
                for j in range(0, len(riserCrvs[i])-1):
                    #if stairs descending
                    rs.MoveObject(riserCrvs[i][j],rs.VectorAdd([0,0,curRiserHeight],-treadVecs[i]))
                    riserGeo = rs.ExtrudeCurveStraight(riserCrvs[i][j],[0,0,0],[0,0,riserHeight])
                    treadGeo = rs.ExtrudeCurveStraight(riserCrvs[i][j],[0,0,0],treadVecs[i])
                    stPt = rs.AddPoint(rs.CurveStartPoint(riserCrvs[i][j]))
                    pt1 = rs.CopyObject(stPt, [0,0,riserHeight]) #first riser in run
                    pt2 = rs.CopyObject(stPt,treadVecs[i]) #last riser in run
                    triCrv = rs.AddPolyline([stPt, pt1, pt2, stPt])
                    triangles.append(rs.AddPlanarSrf(triCrv))
                    geometry.append(riserGeo) #riser
                    geometry.append(treadGeo) #tread
                    curRiserHeight = curRiserHeight + riserHeight
                    rs.MoveObject(riserCrvs[i][j],treadVecs[i])
                    #cleanup
                    rs.DeleteObject(triCrv)
                    rs.DeleteObject(stPt)
                    rs.DeleteObject(pt1)
                    rs.DeleteObject(pt2)
            else:
                for j in range(0, len(riserCrvs[i])-1):
                    #if stairs ascend
                    rs.MoveObject(riserCrvs[i][j],[0,0,curRiserHeight])
                    stPt = rs.AddPoint(rs.CurveStartPoint(riserCrvs[i][j]))
                    pt1 = rs.CopyObject(stPt, [0,0,-riserHeight]) #first riser in run
                    pt2 = rs.CopyObject(stPt,-treadVecs[i]) #last riser in run
                    triCrv = rs.AddPolyline([stPt, pt1, pt2, stPt])
                    triangles.append(rs.AddPlanarSrf(triCrv))
                    riserGeo = rs.ExtrudeCurveStraight(riserCrvs[i][j],[0,0,0],[0,0,-riserHeight])
                    treadGeo = rs.ExtrudeCurveStraight(riserCrvs[i][j],[0,0,0],-treadVecs[i])
                    geometry.append(riserGeo) #riser
                    geometry.append(treadGeo) #tread
                    curRiserHeight = curRiserHeight + riserHeight
                    #cleanup
                    rs.DeleteObject(triCrv)
                    rs.DeleteObject(stPt)
                    rs.DeleteObject(pt1)
                    rs.DeleteObject(pt2)
            
            #Make Stringer
            if (negativeBoo):
                firstStartPt = rs.AddPoint(rs.CurveStartPoint(riserCrvs[i][0]))
                lastStartPt = rs.AddPoint(rs.CurveStartPoint(riserCrvs[i][-2]))
                #rs.MoveObject(firstStartPt, [0,0,riserHeight]) #first riser in run
                rs.MoveObject(lastStartPt,-treadVecs[i]) #last riser in run
                rs.MoveObject(lastStartPt,[0,0,riserHeight]) #last riser in run
            else:
                firstStartPt = rs.AddPoint(rs.CurveStartPoint(riserCrvs[i][0]))
                lastStartPt = rs.AddPoint(rs.CurveStartPoint(riserCrvs[i][-2]))
                rs.MoveObject(firstStartPt, [0,0,-riserHeight]) #first riser in run
                rs.MoveObject(lastStartPt,-treadVecs[i]) #last riser in run
            stringerCrv = rs.AddLine(firstStartPt, lastStartPt)
            stringerSrf = rs.ExtrudeCurveStraight(stringerCrv, [0,0,0], [0,0,-thickness])
            triangles.append(stringerSrf)
            stringer = makeFace(triangles)
            stringerVec = rs.VectorCreate(rs.CurveEndPoint(riserCrvs[i][0]), rs.CurveStartPoint(riserCrvs[i][0]))
            underside = rs.ExtrudeCurveStraight(stringerCrv, rs.CurveStartPoint(riserCrvs[i][0]), rs.CurveEndPoint(riserCrvs[i][0]))
            geometry.append(rs.MoveObject(underside, [0,0,-thickness]))
            geometry.append(rs.CopyObject(stringer, stringerVec))
            geometry.append(stringer)
            
            #cleanup
            rs.DeleteObject(firstStartPt)
            rs.DeleteObject(lastStartPt)
            rs.DeleteObject(stringerCrv)
            rs.DeleteObject(stringerSrf)
        
        #Move Landings
        lastLandingHeight = 0
        for i in range(0, len(segments)-1):
            landingHeight = lastLandingHeight + numRisersPerRun[i]*riserHeight
            rs.MoveObject(landings[i], [0,0,landingHeight])
            landingTopSrf = rs.AddPlanarSrf(landings[i])
            landingBtmSrf = rs.CopyObject(landingTopSrf, [0,0,-thickness])
            geometry.append(landingTopSrf)
            geometry.append(landingBtmSrf)
            lastLandingHeight = landingHeight
            landingEdgesToEx = rs.ExplodeCurves(landings[i])
            geometry.append(rs.ExtrudeCurveStraight(landingEdgesToEx[1], [0,0,0], [0,0,-thickness]))
            geometry.append(rs.ExtrudeCurveStraight(landingEdgesToEx[2], [0,0,0], [0,0,-thickness]))
            rs.DeleteObjects(landingEdgesToEx)
        
        #Create final geometry
        joinedGeo = rs.JoinSurfaces(geometry, True)
        holes = rs.DuplicateSurfaceBorder(joinedGeo)
        cap = rs.AddPlanarSrf(holes)
        newGeo = rs.ExplodePolysurfaces(joinedGeo, True)
        for i in cap:
            newGeo.append(i)
        FinalGeo = rs.JoinSurfaces(newGeo, True)
        
        #cleanup
        try:
            rs.DeleteObjects(segments)
        except:
            rs.DeleteObject(segments)
        rs.DeleteObjects(holes)
        rs.DeleteObjects(landings)
        rs.DeleteObjects(landingEdges)
        for i in riserCrvs:
            rs.DeleteObjects(i)
        
        rs.EnableRedraw(True)
        return FinalGeo
    except:
        print "Error"
        return None

def main():
    if (rs.UnitSystem()==2):
        widthDefault = 1800
        widthMin = 900
        widthMax = 100000
        heightDefault = 5000
        heightMin = 300
    elif (rs.UnitSystem()==4):
        widthDefault = 1.8
        widthMin = .9
        widthMax = 100.0
        heightDefault = 5.0
        heightMin = .30
    elif (rs.UnitSystem()==8):
        widthDefault = 42
        widthMin = 36
        widthMax = 1000.0
        heightDefault = 120
        heightMin = 12
    else:
        print "Change your units to inches"
        return
    
    route = rs.GetObject("Select Stair Guide Curve", rs.filter.curve, True)
    if route is None: return
    
    if 'stair-widthDefault' in sc.sticky:
        widthDefault = sc.sticky['stair-widthDefault']
    if 'stair-heightDefault' in sc.sticky:
        heightDefault = sc.sticky['stair-heightDefault']
    
    width = rs.GetReal("Stair Width", number = widthDefault, minimum = widthMin, maximum = widthMax)
    if width is None: return
    height = rs.GetReal("Stair Height", number = heightDefault, minimum = heightMin)
    if height is None: return
    
    sc.sticky['stair-widthDefault'] = width
    sc.sticky['stair-heightDefault'] = height
    
    try:
        stairGeo = stairHeight(route, width, height)
        result = True
    except:
        result = False
    
    try:
        layers.AddLayerByNumber(401, False)
        layerName = layers.GetLayerNameByNumber(401)
        
        rs.ObjectLayer(stairGeo, layerName)
    except:
        pass
    
    utils.SaveFunctionData('Architecture-Stair', [width, height, str([(pt.X, pt.Y, pt.Z) for pt in rs.CurveEditPoints(route)]), result])
    
    utils.SaveToAnalytics('Architecture-Stair')

if __name__ == "__main__":
    main()
