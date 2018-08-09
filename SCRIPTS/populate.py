import rhinoscriptsyntax as rs
import scriptcontext as sc
import random
import Rhino as rc
import os
import math

import config
import utils

__author__ = 'Tim Williams'
__version__ = "2.0.1"

def Congregate(pts, spacing, loops):
    scaleFactOrig = .1
    for j in range(loops):
        scaleF = ((loops-j)/loops) * scaleFactOrig
        for i, pt in enumerate(pts):
            #PTS TO COMPARE AGAINST
            closest = None
            for comparePt in pts:
                distance = pt.DistanceTo(comparePt)
                if distance == 0: continue
                if distance > spacing*4: continue
                if closest is None or distance<closest[0]:
                    closest = distance, comparePt
            
            if closest is None: continue
            
            vec = rs.VectorCreate(closest[1], pt)
            if closest[0] < spacing:
                vec = rs.VectorReverse(vec)
            
            vec = rs.VectorScale(vec, scaleF)
            pts[i] = pt.Add(pt, vec)
    return pts

def RandomPtsOnSrf(srf, numPts):
    pts = []
    firstPt = RandomPtOnSrf(srf)
    pts.append(firstPt)
    for i in range(1, numPts):
        thisPt = RandomPtOnSrf(srf)
        pts.append(thisPt)
    return pts

def RandomPtOnSrf(srf):
    if srf is None:
        print "Not a surface"
        return
    dom_u = rs.SurfaceDomain(srf, 0)
    dom_v = rs.SurfaceDomain(srf, 1)

    counter = 0
    while True:
        pt_u = random.uniform(dom_u[0], dom_u[1])
        pt_v = random.uniform(dom_v[0], dom_v[1])
        pt = rs.EvaluateSurface(srf, pt_u, pt_v)
        if rs.ObjectType(srf) == 1073741824: #If extrusion objects
            temp = rs.coercesurface(srf)
            testSrf = temp.ToBrep()
        else:
            testSrf = srf
        if rs.IsPointOnSurface(testSrf, pt):
            return pt
        else:
            counter+=1

def TryLoadBlock(type, name):
    if type == '3D People':
        typeFolder = 'People 3D Folder'
    elif type == '2D People':
        typeFolder = 'People 2D Folder'
    elif type == '2D Trees':
        typeFolder = 'Vegetation 2D Folder'    
    
    if rs.IsBlock(name):
        return True
    else:
        folderpath = fileLocations[typeFolder]
        files = os.listdir(folderpath)
        for file in files:
            if os.path.splitext(file)[1] == '.3dm':
                shortName = os.path.splitext(file)[0]
                if shortName == name:
                    filepath = os.path.join(folderpath, file)
                    filepath2 = '"' + filepath + '"'
                    if os.path.isfile(filepath):
                        rs.Command('-_Insert ' + filepath2 + ' B 0 1 0 ', False)
                        objs = rs.SelectedObjects()
                        for obj in objs:
                            rs.DeleteObject(obj)
                        return True

def GetBlockNames(type):
    if type == '3D People':
        typeFolder = 'People 3D Folder'
    elif type == '2D People':
        typeFolder = 'People 2D Folder'
    elif type == '2D Trees':
        typeFolder = 'Vegetation 2D Folder'    
    
    blocks = []
    files = os.listdir(fileLocations[typeFolder])
    for file in files:
        if os.path.splitext(file)[1] == '.3dm':
            blocks.append(os.path.splitext(file)[0])
    return blocks

def GetCustomBlockNames():
    block = rs.BlockNames(True)
    if len(block) < 1:
        print  "There are no blocks in the file"
        return None
    objs = rs.GetObjects('Select block(s) to populate', rs.filter.instance, True)
    if objs is None: return None
    blockNames = []
    for obj in objs:
        if rs.BlockInstanceName(obj) not in blockNames:
            blockNames.append(rs.BlockInstanceName(obj))
    return blockNames

def MoveAwayFromEdges(pts, srf, spacing):
    spacing = spacing*.75
    rhsrf = rs.coercebrep(srf)
    edges = rhsrf.DuplicateNakedEdgeCurves(True, False)
    boundary = rc.Geometry.Curve.JoinCurves(edges)[0]
    tol = rs.UnitAbsoluteTolerance()
    plane = boundary.TryGetPlane()[1]
    for i, pt in enumerate(pts):
        closestPt = boundary.ClosestPoint(pt, spacing)
        if closestPt[0]:
            vec = rs.VectorCreate(pt, boundary.PointAt(closestPt[1]))
            newDist = (spacing)-vec.Length
            if boundary.Contains(pt, plane, tol) == rc.Geometry.PointContainment.Outside:
                vec.Reverse()
                newDist = (spacing)+(vec.Length)
            vec.Unitize()
            pts[i] = pt.Add(pt, vec*newDist)
    return pts

def OrientAwayFromEdges(pts, angles, srf, spacing):
    spacing = spacing
    rhsrf = rs.coercebrep(srf)
    edges = rhsrf.DuplicateNakedEdgeCurves(True, False)
    boundary = rc.Geometry.Curve.JoinCurves(edges)[0]
    tol = rs.UnitAbsoluteTolerance()
    plane = boundary.TryGetPlane()[1]
    for i, pt in enumerate(pts):
        closestPt = boundary.ClosestPoint(pt, spacing)
        if closestPt[0]:
            distance = rs.Distance(pt, boundary.PointAt(closestPt[1]))
            if distance < spacing:
                tangent = boundary.TangentAt(closestPt[1])
                tangent.Reverse()
                angles[i] = VecToAngle(tangent)
                angles[i] += random.uniform(-120, 120)
    return angles

def AngleToVec(angle):
    return rc.Geometry.Vector3d(math.cos(math.radians(angle)), math.sin(math.radians(angle)), 0)

def VecToAngle(vec):
    angle = math.degrees(math.atan2(vec.X, vec.Y))
    if angle<0:
        angle = 180 + (180-abs(angle))
    angle = 450-angle
    if angle >= 360:
        angle = angle - 360
    return angle

def AlignAngles(pts, angles, srf, spacing):
    spacing = spacing*2
    rhsrf = rs.coercebrep(srf)
    edges = rhsrf.DuplicateNakedEdgeCurves(True, False)
    boundary = rc.Geometry.Curve.JoinCurves(edges)[0]
    tol = rs.UnitAbsoluteTolerance()
    plane = boundary.TryGetPlane()[1]
    for i, pt in enumerate(pts):
        currentAngleVec = AngleToVec(angles[i])
        
        #PTS TO COMPARE AGAINST
        closest = None
        for j, comparePt in enumerate(pts):
            distance = pt.DistanceTo(comparePt)
            if distance == 0: continue
            if closest is None or distance<closest[0]:
                closest = distance, comparePt, j
        if closest is None:
            continue
        
        neighborAngleVec = rc.Geometry.Vector3d(math.cos(math.radians(angles[closest[2]])), math.sin(math.radians(angles[closest[2]])), 0)
        
        
        
        newVec = (currentAngleVec+currentAngleVec+neighborAngleVec )/3
        
        angles[i] = VecToAngle(newVec)
    return angles

def RandomAngles(numObjects):
    angles = []
    for each in range(numObjects):
        angles.append(random.uniform(0,360))
    return angles

def Populate_Button():
    try:
        spacing = 42
        ###########################################################################
        #GET FUNCTIONS
        
        #GET INPUT SURFACE
        srf = rs.GetObject('Select surface to populate', rs.filter.surface, True)
        if srf is None: return
        
        #GET NUMBER OF OBJECTS
        if 'populate-numObjects' in sc.sticky:
            numObjectsDefault = sc.sticky['populate-numObjects']
        else:
            numObjectsDefault = 30
        numObjects = rs.GetInteger('Number of objects to populate', numObjectsDefault, 1, 5000)
        if numObjects is None: return
        sc.sticky['populate-numObjects'] = numObjects
        
        #GET POPULATION TYPE
        if 'populate-type' in sc.sticky:
            typeDefault = sc.sticky['populate-type']
        else:
            typeDefault = '3D People'
        types = ['3D People', '2D People', '2D Trees', 'Custom Block']
        type = rs.ListBox(types, "Select block type to populate", "Population Type", typeDefault)
        if type is None: return
        sc.sticky['populate-type'] = type
        
        #GET BLOCK NAMES
        if type == 'Custom Block':
            blockNames = GetCustomBlockNames()
        else:
            blockNames = GetBlockNames(type)
        if blockNames is None: return
        
        ###########################################################################
        #DRAW FUNCTIONS
        rs.EnableRedraw(False)
        
        #RANDOM PTS ON SURFACE
        pts = RandomPtsOnSrf(srf, numObjects)
        
        #RANDOM ANGLES
        angles = RandomAngles(numObjects)
        
        #ORIENT ANGLES AWAY FROM EDGES
        angles = OrientAwayFromEdges(pts, angles, srf, spacing)
        
        for i in range(0, 5):
            #CONGREGATE THE POINTS
            pts = Congregate(pts, spacing, 3)
            
            #MOVE AWAY FROM SURFACE EDGES
            pts = MoveAwayFromEdges(pts, srf, spacing)
        
        #ORIENT ANGLES TOGETHER
        angles = AlignAngles(pts, angles, srf, spacing)
        
        for i, pt in enumerate(pts):
            #Choose random angle
            angle = angles[i]
            
            blockName = blockNames[random.randint(0, len(blockNames)-1)]
            
            if TryLoadBlock(type, blockName):
                eachBlock = rs.InsertBlock(blockName, pt, angle_degrees = angle)
                try:
                    if type == '2D People' or type == '3D People':
                        layerName = '2_ENTOURAGE::' + 'People'
                    elif type == '2D Trees':
                        layerName = '2_ENTOURAGE::' + 'Vegetation'
                    else:
                        layerName = '2_ENTOURAGE'
                    rs.ObjectLayer(eachBlock, layerName)
                    xyScale = random.uniform(.9,1.3)
                    zScale = random.uniform(.9,1.1)
                    rs.ScaleObject(eachBlock, pt, (xyScale,xyScale, zScale))
                except:
                    pass
    
        rs.EnableRedraw(True)
        result = True
    except:
        result = False
    
    utils.SaveFunctionData('Blocks-Populate', [__version__, numObjects, type, result])

if __name__ == "__main__":
    fileLocations = config.GetDict()
    result = Populate_Button()
    if result:
        utils.SaveToAnalytics('Blocks-Populate')