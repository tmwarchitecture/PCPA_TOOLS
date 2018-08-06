import rhinoscriptsyntax as rs
import scriptcontext as sc
import random
import Rhino as rc
import os

import config
import utils

__author__ = 'Tim Williams'
__version__ = "2.0.1"

def Congregate(pts, threshold, loops):
    scaleFactOrig = .1
    for j in range(loops):
        scaleF = ((loops-j)/loops) * scaleFactOrig
        for i, pt in enumerate(pts):
            #PTS TO COMPARE AGAINST
            closest = None
            for comparePt in pts:
                distance = pt.DistanceTo(comparePt)
                if distance == 0: continue
                if closest is None or distance<closest[0]:
                    closest = distance, comparePt
            
            vec = rs.VectorCreate(closest[1], pt)
            if closest[0] < threshold:
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
    spacing = spacing/2
    rhsrf = rs.coercebrep(srf)
    edges = rhsrf.DuplicateNakedEdgeCurves(True, False)
    boundary = rc.Geometry.Curve.JoinCurves(edges)[0]
    for i, pt in enumerate(pts):
        sc.doc.Objects.AddPoint(pt)
        closestPt = boundary.ClosestPoint(pt, spacing)
        if closestPt[0]:
            vec = rs.VectorCreate(pt, boundary.PointAt(closestPt[1]))
            vec.Unitize()
            newDist = (spacing)-vec.Length
            pts[i] = pt.Add(pt, vec*newDist)
    return pts

def Populate_Button():
    #try:
    spacing = 36
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
    numObjects = rs.GetInteger('Number of objects to populate', numObjectsDefault, 1, 500)
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
    
    #CONGREGATE THE POINTS
    pts = Congregate(pts, spacing, 5)
    
    #MOVE AWAY FROM SURFACE EDGES
    pts = MoveAwayFromEdges(pts, srf, spacing)
    
    #ORIENT ANGLES TOGETHER
    
    for pt in pts:
        #Choose random angle
        angle = random.uniform(0,360)
        
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
            except:
                pass

    rs.EnableRedraw(True)
    return True
    #except:
    #    return False

if __name__ == "__main__":
    fileLocations = config.GetDict()
    result = Populate_Button()
    if result:
        utils.SaveToAnalytics('blocks-Populate')
