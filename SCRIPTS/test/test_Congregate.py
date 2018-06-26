import rhinoscriptsyntax as rs
import random



def congregate(objs, threshold, loops):
    scaleFactOrig = .1
    for j in range(loops):
        scaleF = ((loops-j)/loops) * scaleFactOrig
        print scaleF
        for i, pt1 in enumerate(objs):
            tempList = list(objs)
            del tempList[i]
            pt2 = rs.PointClosestObject(pt1, tempList)[1]
            vec = rs.VectorCreate(pt2, pt1)
            dist = rs.Distance(pt2, pt1)
            if dist < threshold:
                vec = rs.VectorReverse(vec)
            vec2 = rs.VectorScale(vec, scaleF)
            rs.MoveObject(pt1, vec2)
            line = rs.AddLine(pt1, pt2)
            rs.DeleteObject(line)
    return objs

def RandomPtOnSrf(srf):
    if srf is None:
        print "Not a surface"
        return
    dom_u = rs.SurfaceDomain(srf, 0)
    dom_v = rs.SurfaceDomain(srf, 1)
    
    while True:
        pt_u = random.uniform(dom_u[0], dom_u[1])
        pt_v = random.uniform(dom_v[0], dom_v[1])
        pt = rs.EvaluateSurface(srf, pt_u, pt_v)
        if rs.IsPointOnSurface(srf, pt):
            return pt

def RandomPtsOnSrf(srf, numPts):
    pts = []
    firstPt = RandomPtOnSrf(srf)
    pts.append(firstPt)
    for i in range(1, numPts):
        thisPt = RandomPtOnSrf(srf)
        #rs.PointArrayClosestPoint(
        pts.append(thisPt)
    return pts

def EdgeVectors(srf, pts):
    crvs = rs.DuplicateEdgeCurves(srf)
    edgeVectors = []
    for pt in pts:
        closestIndex = 0
        closestDist = 99999
        for i, crv in enumerate(crvs):
            tempPt = rs.EvaluateCurve(crv, rs.CurveClosestPoint(crv, pt))
            dist = rs.Distance(pt, tempPt)
            if dist < closestDist:
                closestDist = dist
                closestIndex = i
        
        tempPt = rs.EvaluateCurve(crvs[closestIndex], rs.CurveClosestPoint(crvs[closestIndex], pt))
        rs.AddLine(tempPt, pt)
        edgeVectors.append(rs.VectorCreate(tempPt, pt))
    return edgeVectors


threshold = 3

srf = rs.VisibleObjects()

myPts = RandomPtsOnSrf(srf, 10)

newPts = rs.AddPoints(myPts)

vecs = EdgeVectors(srf, newPts)
for vec in vecs:
    print rs.VectorLength(vec)
for i, pt in enumerate(newPts):
    rs.MoveObject(pt, rs.VectorScale(vecs[i], .5))

#pts = congregate(newPts, threshold, 50)

#for pt in pts:
#    rs.AddCircle(pt, threshold/2)