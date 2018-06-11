import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
from utils import GetDatePrefix
import layers
import utils

def SuperExplodeBlock():
    block = rs.GetObject("Select block to explode", rs.filter.instance, preselect = True)
    if block is None: return
    objs = rs.ExplodeBlockInstance(block, True)
    return objs

def RenameBlockCmd():
    block = rs.GetObject("Select block to rename", filter = 4096, preselect = True)

    #Default Name
    try:
        number = int(rs.BlockInstanceName(block).split('_')[-1])
        number += 1
        if len(str(number))<2:
            numString = '0' + str(number)
        else:
            numString = str(number)
    except:
        numString = '01A'
    defaultName = GetDatePrefix() + "_OPTION_" + numString

    looping = True
    while looping:
        newName = rs.StringBox("Enter new block name", default_value = defaultName, title = 'Rename Block')
        if newName is None: return
        if rs.IsBlock(newName):
            print "Block name already exists"
        elif len(newName) == 0:
            print "Must specify a name"
            pass
        else:
            looping = False

    return rs.RenameBlock(rs.BlockInstanceName(block), newName)

def ReplicateBlock(blockObj):
    #Check if a block
    try:
        if rs.IsBlockInstance(blockObj):
            pass
        else:
            return
    except:
        return

    #Copy block
    copiedBlock = rs.CopyObject(blockObj)


    #Get new block name
    try:
        number = int(rs.BlockInstanceName(copiedBlock).split('_')[-1])
        number += 1
        if len(str(number))<2:
            numString = '0' + str(number)
        else:
            numString = str(number)
    except:
        numString = '01A'
    defaultName = GetDatePrefix() + "_OPTION_" + numString
    newBlockName = rs.StringBox("Name for new Block", defaultName, 'Make Block Unique')
    if newBlockName is None: return

    #Get previous base point
    xform = rs.BlockInstanceXform(copiedBlock)
    basePoint = rs.BlockInstanceInsertPoint(copiedBlock)

    #Explode block
    objsInside = rs.ExplodeBlockInstance(copiedBlock)

    rs.AddBlock(objsInside, basePoint, newBlockName, True)

    #Create new block
    return rs.InsertBlock2(newBlockName, xform)

def MakeBlockUnique():
    block = rs.GetObject("Select block to make unique", rs.filter.instance, preselect = True)
    if block is None: return

    #Default Name
    try:
        number = int(rs.BlockInstanceName(block).split('_')[-1])
        number += 1
        if len(str(number))<2:
            numString = '0' + str(number)
        else:
            numString = str(number)
    except:
        numString = '01A'
    defaultName = GetDatePrefix() + "_OPTION_" + numString

    looping = True
    while looping:
        newName = rs.StringBox("Enter new block name", default_value = defaultName, title = 'MakeUnique')
        if newName is None: return
        if rs.IsBlock(newName):
            print "Block name already exists"
        elif len(newName) == 0:
            print "Must specify a name"
            pass
        else:
            looping = False

    if newName is None: return
    rs.EnableRedraw(False)
    xform = rs.BlockInstanceXform(block)
    insertPt = rs.BlockInstanceInsertPoint(block)
    objs = rs.ExplodeBlockInstance(block, False)
    rs.TransformObjects(objs, rs.XformInverse(xform))
    pt = rs.TransformObject(insertPt, rs.XformInverse(xform))
    rs.AddBlock(objs, insertPt, newName, True)
    newBlock = rs.InsertBlock2(newName, xform)
    rs.DeleteObject(pt)
    rs.EnableRedraw(True)
    rs.SelectObject(newBlock)

def Iterate():
    block = rs.GetObject("Select Design Option Block to iterate", rs.filter.instance, True)
    if block is None: return
    newBlock = ReplicateBlock(block)
    try:
        optionLayers = layers.AddSpecificLayer(3000, False)

        try:
            rootLayer = optionLayers[0]
        except:
            rootLayer = optionLayers


        color = rs.LayerColor(rootLayer)
        layerName = rs.BlockInstanceName(newBlock)

        newBlockLayer = rs.AddLayer(layerName,color = color , parent = rootLayer)

        rs.ObjectLayer(newBlock, newBlockLayer)
        rs.CurrentLayer(newBlockLayer)
        prevBlockLayer = rs.ObjectLayer(block)
        try:
            prevBlockLayerRoot = prevBlockLayer.split('::')[0]
            if prevBlockLayerRoot == rootLayer:
                rs.LayerVisible(prevBlockLayer, False)
        except:
            pass
    except:
        pass

def ResetBlockScale():
    blocks = rs.GetObjects("Select blocks to reset", rs.filter.instance, preselect = True)
    if blocks is None: return

    points = [
     rg.Point3d(0,0,0),
     rg.Point3d(1,0,0),
     rg.Point3d(0,1,0),
     rg.Point3d(0,0,1)
    ]

    for block in blocks:
        xform = rs.BlockInstanceXform(block)
        namne = rs.BlockInstanceName(block)

        pts = rg.Polyline(points)

        pts.Transform(xform)

        finalOrigin = pts[1]
        finalXaxis = rs.VectorSubtract( pts[1], pts[0] )
        finalYaxis = rs.VectorSubtract( pts[2], pts[0] )
        finalPlane = rg.Plane(finalOrigin, finalXaxis, finalYaxis)


        xFac = 1 / rs.Distance(pts[1],pts[0])
        yFac = 1 / rs.Distance(pts[2],pts[0])
        zFac = 1 / rs.Distance(pts[3],pts[0])


        newXForm = rg.Transform.Scale(finalPlane, xFac, yFac, zFac)
        rs.TransformObject(block,newXForm)


if __name__ == "__main__":
    func = rs.GetInteger("", 0, 0, 100)

    if func == 0:
        Iterate()
        utils.SaveToAnalytics('blocks-iterate')
    elif func == 1:
        MakeBlockUnique()
        utils.SaveToAnalytics('blocks-Make Unique')
    elif func == 2:
        SuperExplodeBlock()
        utils.SaveToAnalytics('blocks-Super Explode')
    elif func == 3:
        RenameBlockCmd()
        utils.SaveToAnalytics('blocks-Rename Block')
    elif func == 4:
        ResetBlockScale()
        utils.SaveToAnalytics('blocks-Reset Block Scale')
    else:
        print "No function found"