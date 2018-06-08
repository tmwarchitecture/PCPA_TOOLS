#k-means points
import rhinoscriptsyntax as rs
import random
def getMeanPt(pts):
    ptCoords = []
    for i in range(0,len(pts)):    
        ptCoords.append( rs.PointCoordinates(pts[i]))
    meanPt = ptCoords[0]
    for i in range(1,len(pts)):
        meanPt = meanPt + ptCoords[i]
    meanPt = meanPt/len(pts)
    return rs.coerce3dpoint(meanPt)

def partitionPts (centroids, allPts):
    partitionedPts = []
    #for i in range(0,len(centroids)):
        #partitionedPts.append([])
    indexList = []
    for i in range(0,len(allPts)):
        indexList.append(rs.PointArrayClosestPoint(centroids,allPts[i]))
    for i in range(0,len(centroids)):
        tempList = []
        for j in range(0,len(allPts)):
            if(indexList[j]==i):
                tempList.append(allPts[j])
        partitionedPts.append(tempList)
    return partitionedPts #returns a list of lists of pt GUIDS

def bbox2pt(pts):
    ptCoords = []
    twoPts=[[999999, 999999, 999999],[-99999, -99999, -99999]]
    for i in range(0,len(pts)):
        ptCoords = rs.PointCoordinates(pts[i])
        if(ptCoords.X<twoPts[0][0]):
            twoPts[0][0] = ptCoords.X
        if(ptCoords.Y<twoPts[0][1]):
            twoPts[0][1] = ptCoords.Y
        if(ptCoords.Z<twoPts[0][2]):
            twoPts[0][2] = ptCoords.Z
        if(ptCoords.X>twoPts[1][0]):
            twoPts[1][0] = ptCoords.X
        if(ptCoords.Y>twoPts[1][1]):
            twoPts[1][1] = ptCoords.Y
        if(ptCoords.Z>twoPts[1][2]):
            twoPts[1][2] = ptCoords.Z
    return twoPts

def kMeansPts(k, allPts):
    #rs.EnableRedraw(False)
    centroids = []
    ptLists = []
    tempCent = []
    delta = []
    kMeansPts.finalCentroids = []
    finalPts = []
    min = bbox2pt(allPts)[0]
    max = bbox2pt(allPts)[1]
    xMin = min[0]
    yMin = min[1]
    zMin = min[2]
    xMax = max[0]
    yMax = max[1]
    zMax = max[2]
    for i in range(0,k):
        centroids.append(rs.AddPoint(random.uniform(xMin, xMax),random.uniform(yMin, yMax),random.uniform(zMin, zMax)))
        tempCent.append(rs.PointCoordinates(centroids[i]))
        delta.append(100)
    ########################################
    cont = True
    while (cont):
        ptLists = partitionPts(centroids, allPts)
        if (rs.IsPoint(centroids[0])):
            rs.DeleteObjects(centroids)
        for j in range(0,k):
            if (len(ptLists[j])<1):
                print ("Attempt Failed")
                return None
            centroids[j] = (getMeanPt(ptLists[j]))
            delta[j] = rs.Distance(rs.coerce3dpoint(tempCent[j]), centroids[j])
        for j in range(0,k):
            if (delta[j]<.1):
                cont = False
            else:
                break
        for j in range(0,k):
            tempCent[j] = centroids[j]
    for j in range(0,k): #final centroids
        kMeansPts.finalCentroids.append(rs.AddPoint(centroids[j]))
        rs.ObjectColor(kMeansPts.finalCentroids[j], [0,255,0])
    for j in range(0,k): #final ptlist groups
        color = [random.randint(100,255), random.randint(100,255), random.randint(100,255)]
        tempList = []
        for i in range (0,len(ptLists[j])):
            tempList.append(rs.AddPoint(ptLists[j][i]))
            rs.ObjectColor(tempList[i],color)
        finalPts.append(tempList)
    rs.DeleteObjects(allPts)
    #rs.EnableRedraw(True)
    return None

def main():
    ptList = rs.GetObjects("Select Points", 1)
    x = kMeansPts(1, ptList)
    print "A"
    #rs.AddCircle(kMeansPts.finalCentroids[0], 10)

main()