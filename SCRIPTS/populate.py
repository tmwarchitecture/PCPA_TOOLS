import rhinoscriptsyntax as rs
import random
import config
import os

import utils

fileLocations = config.GetDict()

def RandomPtsOnSrf(srf, numPts):
    pts = []
    firstPt = RandomPtOnSrf(srf)
    pts.append(firstPt)
    for i in range(1, numPts):
        thisPt = RandomPtOnSrf(srf)
        #rs.PointArrayClosestPoint(
        pts.append(thisPt)
    return pts

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

def TryLoadBlock(type, name):
    if rs.IsBlock(name):
        return True
    else:
        folderpath = fileLocations[type]
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

def RandomBlock(type):
    if type == 'Custom Block':
        block = rs.BlockNames(True)
        if len(block) < 1: 
            return None
        obj = rs.GetObject('Select block to populate', rs.filter.instance, True)
        if obj is None: return
        name = rs.BlockInstanceName(obj)
        return name
    else:
        blocks = []
            
        files = os.listdir(fileLocations[type])
        for file in files:
            if os.path.splitext(file)[1] == '.3dm':
                blocks.append(os.path.splitext(file)[0])

    index = random.randint(0, len(blocks)-1)
    return blocks[index]

def main():
    srf = rs.GetSurfaceObject('Select surface to populate', True)[0]
    if srf is None: return
    
    numObjects = rs.GetInteger('Number of objects to populate', 30, 1, 500)
    if numObjects is None: return
    
    types = ['3D People', '2D People', '2D Trees', 'Custom Block']
    type = rs.ListBox(types, "Select block type to populate", "Placer", types[0])
    if type is None: return
    
    if type == '3D People':
        type = 'People 3D Folder'
    elif type == '2D People':
        type = 'People 2D Folder'
    elif type == '2D Trees':
        type = 'Vegetation 2D Folder'
    
    rs.EnableRedraw(False)
    
    pts = RandomPtsOnSrf(srf, numObjects)
    
    blockName = RandomBlock(type)
    
    for pt in pts:
        angle = random.uniform(0,360)
        
        if type != 'Custom Block':
            blockName = RandomBlock(type)
        if blockName is None:
            print "No blocks in document"
            return
        
        if TryLoadBlock(type, blockName):
            rs.InsertBlock(blockName, pt, angle_degrees = angle)
    
    rs.EnableRedraw(True)

if __name__ == "__main__":
    main()
    utils.SaveToAnalytics('blocks-Populate')