 import rhinoscriptsyntax as rs

def roundedDist2(numList, multiple):
    """
    :param numList: list of floats to round
    :param decPlaces: number of decimals to round to (-1 = 10, 2 = .01)
    :return: modified list of numbers
    """
    newList = []
    for num in numList:
        if num<0:
            negBool = True
        else:
            negBool = False
        
        val = int(abs(num)/multiple)*multiple
        
        if val == 0:
            val = multiple
        
        if negBool:
            val *= -1
        
        newList.append(val)
    return newList

def rectify(pline, decPlaces):
    """
    --Uses your current cplane as guides
    pline: one pline to rectify
    decPlace: number of decimals to round to (1 = 100mm, 2 = 10mm, 3 = 1mm)
    """
    
    #Remove colinear points
    rs.SimplifyCurve(pline)
    
    #orient to world
    xPt = rs.VectorAdd(rs.ViewCPlane().Origin, rs.ViewCPlane().XAxis)
    yPt = rs.VectorAdd(rs.ViewCPlane().Origin, rs.ViewCPlane().YAxis)
    origCplane = [rs.ViewCPlane().Origin, xPt , yPt]
    world = [[0,0,0], [1,0,0], [0,1,0]] 
    rs.OrientObject(pline, origCplane, world)
    
    #get ctrl Pts
    ctrlPts = rs.CurvePoints(pline)
    
    #test if closed
    closedBool = rs.IsCurveClosed(pline)
    if closedBool:
        del ctrlPts[-1]
    
    #initial direction
    stPt = ctrlPts[0]
    nxtPt = ctrlPts[1]
    dX = abs(stPt[0]-nxtPt[0])
    dY = abs(stPt[1]-nxtPt[1])
    if dX>dY:
        xDir = True
    else:
        xDir = False
    
    #split into x and y vals
    xVals = []
    yVals = []
    xVals.append(ctrlPts[0][0])
    yVals.append(ctrlPts[0][1])
    if xDir:
        for i in range(1, len(ctrlPts)):
            if i%2==1:
                xVals.append(ctrlPts[i][0])
            else:
                yVals.append(ctrlPts[i][1])
    else:
        for i in range(1, len(ctrlPts)):
            if i%2==0:
                xVals.append(ctrlPts[i][0])
            else:
                yVals.append(ctrlPts[i][1])
    
    xVals = roundedDist2(xVals, decPlaces)
    yVals = roundedDist2(yVals, decPlaces)
    
    
    #Make points
    newPts = []
    for i in range(0, len(ctrlPts)):
        if xDir:
            if i%2==0:
                newPts.append(rs.coerce3dpoint([xVals[int(i/2)], yVals[int(i/2)], 0]))
            else:
                newPts.append(rs.coerce3dpoint([xVals[int(i/2+.5)], yVals[int(i/2-.5)], 0]))
        else:
            if i%2==0:
                newPts.append(rs.coerce3dpoint([xVals[int(i/2)], yVals[int(i/2)], 0]))
            else:
                newPts.append(rs.coerce3dpoint([xVals[int(i/2-.5)], yVals[int(i/2+.5)], 0]))
    
    #Close it
    if closedBool:
        if xDir:
            newPts[-1].X = newPts[0].X
        else:
            newPts[-1].Y = newPts[0].Y
        newPts.append(newPts[0])
    
    #make new Line
    newLine = rs.AddPolyline(newPts)
    
    #Cleanup
    objectsLay = rs.MatchObjectAttributes(newLine, pline)
    rs.ObjectColor(pline, (255,0,0))
    rs.DeleteObject(pline)
    
    #Move back to original cplane
    rs.OrientObject(newLine, world, origCplane)
    return newLine

def main():
    objs = rs.GetObjects("Select Curves to Rectify", preselect = True, filter = 4)
    if objs is None:
        return
    decPlaces = rs.GetInteger('Round to multiple (e.g. 3 = 3 inches)', number = 1, minimum = 1)
    
    rs.EnableRedraw(False)
    for obj in objs:
        try:
            newLine = rectify(obj, decPlaces)
        except:
            print "Rectify failed"
    rs.EnableRedraw(True)

if __name__=="__main__":
    main()
