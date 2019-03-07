import rhinoscriptsyntax as rs
import scriptcontext as sc
import random
import Rhino as rc
import os
import math
import layers

import config
import utils

__author__ = 'Tim Williams'
__version__ = "2.2.0"

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
        
        if type(srf) == rc.DocObjects.ObjectType.Extrusion: #If extrusion objects
            temp = rs.coercesurface(srf)
            testSrf = temp.ToBrep()
        else:
            testSrf = srf
        testPt = testSrf.ClosestPoint(pt)
        d = rs.Distance(testPt, pt)
        if d > rs.UnitAbsoluteTolerance():
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
    elif type == '3D Trees':
        typeFolder = 'Vegetation 3D Folder'
    elif type == '3D Vehicles':
        typeFolder = 'Vehicle 3D Folder'

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
    elif type == '3D Trees':
        typeFolder = 'Vegetation 3D Folder'
    elif type == '3D Vehicles':
        typeFolder = 'Vehicle 3D Folder'

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
    if objs is None: return None, None
    blockNames = []
    for obj in objs:
        blockNames.append(rs.BlockInstanceName(obj))
    return blockNames, objs

def MoveAwayFromEdges(pts, srf, spacing):
    spacing = spacing*.75
    test = srf.ToBrep()
    edges = test.DuplicateNakedEdgeCurves(True, False)
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
    #rhsrf = rs.coercebrep(srf)
    test = srf.ToBrep()
    edges = test.DuplicateNakedEdgeCurves(True, False) #<----------
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
    #rhsrf = rs.coercebrep(srf)
    test = srf.ToBrep()
    edges = test.DuplicateNakedEdgeCurves(True, False)
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

def GetNumObjects():
    if 'populate-numObjects' in sc.sticky:
        numObjectsDefault = sc.sticky['populate-numObjects']
    else:
        numObjectsDefault = 30
    numObjects = rs.GetInteger('Number of objects to populate', numObjectsDefault, 1, 5000)
    if numObjects is None: return
    sc.sticky['populate-numObjects'] = numObjects
    return numObjects

def GetPopulationType(vehicles = True):
    if 'populate-type' in sc.sticky:
        typeDefault = sc.sticky['populate-type']
    else:
        typeDefault = '3D People'
    types = ['3D People', '2D People', '3D Trees', '2D Trees', 'Custom Block']
    if vehicles:
        types.insert(-1, '3D Vehicles')
    type = rs.ListBox(types, "Select block type to populate", "Population Type", typeDefault)
    if type is None: return None
    sc.sticky['populate-type'] = type
    return type

def GetCustomSpacing(blockName):
    guids = rs.BlockObjects(blockName)
    pts = rs.BoundingBox(guids)
    return rs.Distance(pts[0], pts[2])

#################################################################
def PopulatePath():
    numObjects = 0
    type = None
    try:
        crvs = rs.GetObjects("Select curves to populate", rs.filter.curve, True)
        if crvs is None: return None
        crvObjs = []
        for crv in crvs:
            crvObjs.append(rs.coercecurve(crv))
        
        #GET POPULATION TYPE
        type = GetPopulationType()
        if type is None: return None
        
        #GET BLOCK NAMES
        if type == 'Custom Block':
            blockNames, instances = GetCustomBlockNames()
        else:
            blockNames = GetBlockNames(type)
        if blockNames is None: return
        
        #GET NUMBER OF OBJECTS
        numObjects = GetNumObjects()
        if numObjects is None: return None
        
        rs.EnableRedraw(False)
        if type == '2D People' or type == '3D People':
            spacing = 42
        elif type == '2D Trees':
            spacing = 100
        elif type == '3D Trees':
            spacing = 200
        elif type == '3D Vehicles':
            spacing = 240
        else:
            spacing = GetCustomSpacing(blockNames[0]) #currently just selects the first block
        
        #GET PTS
        upVec = rc.Geometry.Vector3d(0,0,1)
        plane0 = rc.Geometry.Plane(rc.Geometry.Point3d(0,0,0),  upVec)
        plane0.Rotate(math.pi/2, upVec)
        crvData = []
        for i, crvObj in enumerate(crvObjs):
            lengths = []
            frames = []
            curveLength = crvObj.GetLength()
            counter = 0
            
            while len(frames) < numObjects:
                t = utils.Remap(random.uniform(0,1), 0, 1, 0, curveLength)
                
                posOkay = True
                if len(lengths)>0:
                    counter+=1
                    for eachPrevPos in lengths:
                        if abs(eachPrevPos-t) < spacing:
                            posOkay = False
                
                if posOkay:
                    lengths.append(t)
                    pt = crvObj.PointAtLength(t)
                    param = crvObj.LengthParameter(t)[1]
                    tan = crvObj.TangentAt(param)
                    xAxis = rc.Geometry.Vector3d.CrossProduct(tan, upVec)
                    xAxis.Reverse()
                    frames.append(rc.Geometry.Plane(pt, tan, xAxis))
                
                if counter > int(curveLength/numObjects):
                    print "Curve {}: Could only fit {} of the requested {} objects".format(i, len(frames), numObjects)
                    break
            crvData.append(frames)
        
        scaleVariation = .1
        #PLACE THE BLOCKS
        for i, crvObj in enumerate(crvObjs):
            for i, frame in enumerate(crvData[i]):
                blockName = blockNames[random.randint(0, len(blockNames)-1)]
                if TryLoadBlock(type, blockName):
                    xform = rc.Geometry.Transform.PlaneToPlane(plane0, frame)
                    eachBlock = rs.InsertBlock2(blockName, xform)
                    try:
                        if type == '2D People' or type == '3D People':
                            layerName = layers.GetLayerNameByNumber(2200)
                        elif type == '2D Trees' or type == '3D Trees':
                            layerName = layers.GetLayerNameByNumber(2300)
                        elif type == '3D Vehicles':
                            layerName = layers.GetLayerNameByNumber(2400)
                        elif type == 'Custom Block':
                            layerName = rs.ObjectLayer(instances[0])
                        else:
                            layers.AddLayerByNumber(2000)
                            layerName = layers.GetLayerNameByNumber(2000)
                        rs.ObjectLayer(eachBlock, layerName)
                        
                        if type != '3D Vehicles':
                            xyScale = random.uniform(1-scaleVariation,1+scaleVariation)
                            zScale = random.uniform(1-scaleVariation,1+scaleVariation)
                        else:
                            xyScale = 1
                            zScale = 1
                        rs.ScaleObject(eachBlock, frame, (xyScale,xyScale, zScale))
                    except:
                        pass
        rs.EnableRedraw(True)
        result = True
    except:
        result = False
    
    utils.SaveFunctionData('Blocks-Populate Path', [__version__, numObjects, type, result])

#################################################################
def Populate_Surfaces():
    #try:
    ###########################################################################
    #GET FUNCTIONS
    
    #GET INPUT SURFACE
    #srfs = rs.GetObjects('Select surface to populate', rs.filter.surface, True, True)
    #if srfs is None: return
    
    msg="Select a surface or polysurface face to populate"
    srf_filter= rc.DocObjects.ObjectType.Surface
    res,srfObjs=rc.Input.RhinoGet.GetMultipleObjects(msg,False,srf_filter)
    if res!=rc.Commands.Result.Success: return        
    
    #Cleanup obj ref
    srfs = []
    for srf in srfObjs:
        if srf.GeometryComponentIndex < 0:
            face=srf.Surface()
        else:
            face=srf.Face()
        subSrf=face.ToNurbsSurface()
        srfs.append(subSrf)
    
    #GET POPULATION TYPE
    type = GetPopulationType(False)
    if type is None: return None
    
    #GET BLOCK NAMES
    if type == 'Custom Block':
        blockNames, blockIDs = GetCustomBlockNames()
    else:
        blockNames = GetBlockNames(type)
    if blockNames is None: return
    
    #GET NUMBER OF OBJECTS
    numObjects = GetNumObjects()
    if numObjects is None: return None
    
    ###########################################################################
    #Spacing
    if type == '2D People' or type == '3D People':
        spacing = 42
    elif type == '2D Trees':
        spacing = 100
    elif type == '3D Trees':
        spacing = 200
    else:
        spacing = GetCustomSpacing(blockNames[0])
    ###########################################################################
    
    #DRAW FUNCTIONS
    rs.EnableRedraw(False)
    
    #RANDOM PTS ON SURFACE
    pts = []
    for srf in srfs:
        pts.append(RandomPtsOnSrf(srf, numObjects))
    
    #RANDOM ANGLES
    angles = []
    for srf in srfs:
        angles.append(RandomAngles(numObjects))
    
    #ORIENT ANGLES AWAY FROM EDGES
    if type == '2D People' or type == '3D People':
        for i, srf in enumerate(srfs):
            angles[i] = OrientAwayFromEdges(pts[i], angles[i], srf, spacing)
    
    for i in range(0, 5):
        #CONGREGATE THE POINTS
        for j, srf in enumerate(srfs):
            pts[j] = Congregate(pts[j], spacing, 3)
            
            #MOVE AWAY FROM SURFACE EDGES
            pts[j] = MoveAwayFromEdges(pts[j], srf, spacing)
    
    #ORIENT ANGLES TOGETHER
    if type == '2D People' or type == '3D People':
        for i, srf in enumerate(srfs):
            angles[i] = AlignAngles(pts[i], angles[i], srf, spacing)
    
    upVec = rc.Geometry.Vector3d(0,0,1)
    scaleVariation = .1
    
    for i, srf in enumerate(srfs):
        for j, pt in enumerate(pts[i]):
            #Choose random angle
            angle = angles[i][j]
            
            thisIndex = random.randint(0, len(blockNames)-1)
            thisBlockName = blockNames[thisIndex]
            
            if TryLoadBlock(type, thisBlockName):
                #xform = rs.BlockInstanceXform(blockIDs[thisIndex])
                eachBlock = rs.InsertBlock(thisBlockName, pt, angle_degrees = angle)
                #eachBlock = rs.InsertBlock2(thisBlockName, newXform)
                try:
                    if type == '2D People' or type == '3D People':
                        layerName = '2_ENTOURAGE::' + 'People'
                    elif type == '2D Trees':
                        layerName = '2_ENTOURAGE::' + 'Vegetation'
                    elif type == '3D Trees':
                        layerName = '2_ENTOURAGE::' + 'Vegetation'
                    elif type == '3D Vehicles':
                        layerName = '2_ENTOURAGE::' + 'Vehicles'
                    elif type == 'Custom Block':
                        layerName = rs.ObjectLayer(blockIDs[0])
                    else:
                        layerName = '2_ENTOURAGE'
                    rs.ObjectLayer(eachBlock, layerName)
                    xyScale = random.uniform(1-scaleVariation,1+scaleVariation)
                    zScale = random.uniform(1-scaleVariation,1+scaleVariation)
                    rs.ScaleObject(eachBlock, pt, (xyScale,xyScale, zScale))
                except:
                    pass
    
    rs.EnableRedraw(True)
    #    result = True
    #except:
    #    result = False
    
    #utils.SaveFunctionData('Blocks-Populate', [__version__, numObjects, type, result])

if __name__ == "__main__" and utils.IsAuthorized():
    func = rs.GetInteger("func num")
    if func == 0:
        fileLocations = config.GetDict()
        result = Populate_Surfaces()
        if result:
            utils.SaveToAnalytics('Blocks-Populate')
    elif func == 1:
        fileLocations = config.GetDict()
        result = PopulatePath()
        if result:
            utils.SaveToAnalytics('Blocks-Populate Path')
