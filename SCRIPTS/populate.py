import rhinoscriptsyntax as rs
import random
import config
import os

import utils

__author__ = 'Tim Williams'
__version__ = "2.0.0"

def congregate(objs, threshold, loops):
    scaleFactOrig = .1
    for j in range(loops):
        scaleF = ((loops-j)/loops) * scaleFactOrig
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
    try:
        srf = rs.GetObject('Select surface to populate', rs.filter.surface, True)
        #srf = rs.GetSurfaceObject('Select surface to populate', True)
        if srf is None: return
        #srf = srf[0]

        numObjects = rs.GetInteger('Number of objects to populate', 30, 1, 500)
        if numObjects is None: return

        types = ['3D People', '2D People', '2D Trees', 'Custom Block']
        type = rs.ListBox(types, "Select block type to populate", "Population Type", types[0])
        if type is None: return

        if type == '3D People':
            type = 'People 3D Folder'
        elif type == '2D People':
            type = 'People 2D Folder'
        elif type == '2D Trees':
            type = 'Vegetation 2D Folder'

        rs.EnableRedraw(False)

        pts = RandomPtsOnSrf(srf, numObjects)

        realPts = rs.AddPoints(pts)
        congregate(realPts, 36, 5)

        blockName = RandomBlock(type)

        for pt in realPts:
            angle = random.uniform(0,360)


            if type != 'Custom Block':
                blockName = RandomBlock(type)
            if blockName is None:
                print "No blocks in document"
                return

            if TryLoadBlock(type, blockName):
                eachBlock = rs.InsertBlock(blockName, pt, angle_degrees = angle)
                try:
                    if type == 'People 2D Folder' or type == 'People 3D Folder':
                        layerName = '2_ENTOURAGE::' + 'People'
                    elif type == 'Vegetation 2D Folder':
                        layerName = '2_ENTOURAGE::' + 'Vegetation'
                    else:
                        layerName = '2_ENTOURAGE'
                    rs.ObjectLayer(eachBlock, layerName)
                except:
                    pass

        try:
            rs.DeleteObjects(realPts)
        except:
            pass

        rs.EnableRedraw(True)
        return True
    except:
        return False

if __name__ == "__main__":
    fileLocations = config.GetDict()
    result = main()
    if result:
        utils.SaveToAnalytics('blocks-Populate')
