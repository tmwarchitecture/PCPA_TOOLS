import rhinoscriptsyntax as rs
from utils import GetDatePrefix
import layers

def SuperExplodeBlock():
    block = rs.GetObject("Select block to explode", filter = 4096, preselect = True)
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
        numString = '01a'
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
    block = rs.GetObject("Select block to make unique", filter = 4096, preselect = True)
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
        numString = '01a'
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
        optionLayer = layers.AddSpecificLayer(3000, False)[0]
        color = rs.LayerColor(optionLayer)
        newBlockLayer = rs.AddLayer(rs.BlockInstanceName(newBlock),color = color , parent = optionLayer)
        rs.ObjectLayer(newBlock, newBlockLayer)
        rs.CurrentLayer(newBlockLayer)
        prevBlockLayer = rs.ObjectLayer(block)
        rs.LayerVisible(prevBlockLayer, False)
    except:
        pass

if __name__ == "__main__":
    func = rs.GetInteger("", 0, 0, 100)
    if func == 0:
        Iterate()
    elif func == 1:
        MakeBlockUnique()
    elif func == 2:
        SuperExplodeBlock()
    elif func == 3:
        RenameBlockCmd()
    else:
        print "No function found"