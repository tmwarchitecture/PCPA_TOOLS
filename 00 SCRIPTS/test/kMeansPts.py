import rhinoscriptsyntax as rs
import Rhino as rc
import random

def getMeanPt(pts):
    pt_sum = rs.PointCoordinates(pts[0])
    for i in xrange(1, len(pts)):
        pt_sum += rs.PointCoordinates(pts[i])
    pt_sum = pt_sum / len(pts)    
    return pt_sum

def partitionPts (centroids, allPts):
    partitionedPts = []
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

def kMeansPts(k, allPts, colorPts = True):
    """kMeansPts(k, allPts, colorPts = True)
    inputs:
        k (int): number of partitions
        allPts (list guids): points to partition
        colorPts (boolean)(optional)    : Randomly color the groups or not
    return:
        [0] = partitioned guids
        [1] = new centroids of paritioned list (point3d)
    """
    centroids = []
    ptLists = []
    tempCent = []
    delta = []
    kMeansPts.finalCentroids = []
    finalPts = []
    
    random.seed(1000)
    ########################################
    newBB = rs.BoundingBox(allPts)
    min = newBB[0]
    max = newBB[6]
    ########################################
    for i in range(0,k):
        centroids.append(rc.Geometry.Point3d(random.uniform(min.X, max.X),random.uniform(min.Y, max.Y),random.uniform(min.Z, max.Z)))
        tempCent.append(centroids[i])
        delta.append(100)#<---ODD NUMBER HERE
    ########################################
    cont = True
    while (cont):
        ptLists = partitionPts(centroids, allPts)
        for j in range(0,k):
            if (len(ptLists[j])<1):
                return None
            centroids[j] = (getMeanPt(ptLists[j]))
            delta[j] = rs.Distance(tempCent[j], centroids[j])
        for j in range(0,k):
            if (delta[j]<.1): #<---ODD NUMBER HERE
                cont = False
            else:
                break
        for j in range(0,k):
            tempCent[j] = centroids[j]
    ########################################
    #JUST COLORING THE POINTS
    for each in ptLists:
        color = [random.randint(100,255), random.randint(100,255), random.randint(100,255)]
        for eachPt in each:
            rs.ObjectColor(eachPt, color)
    
    return ptLists, centroids

def kMeansPts_Main():
    ptList = rs.GetObjects("Select Points", 1)
    if ptList is None: return
    
    x = kMeansPts(2, ptList, True)

if __name__ == "__main__":
    kMeansPts_Main()