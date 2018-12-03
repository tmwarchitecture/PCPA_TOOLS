#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
from utils import GetDatePrefix
import layers
import utils

__author__ = 'Tim Williams'
__version__ = "2.1.0"

def SuperExplodeBlock():
    try:
        blocks = rs.GetObjects("Select blocks to explode", rs.filter.instance, preselect = True)
        if blocks is None: return
        objs = []
        for block in blocks:
            objs.append(rs.ExplodeBlockInstance(block, True))
        return objs
    except:
        return None

def RenameBlockButton():
    try:
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
    except:
        return None

##############################################################################
#Make Block Unique
def MakeBlockUnique(block, newName):
    """
    Explodes a block and makes a new one with 'newName'
    """
    xform = rs.BlockInstanceXform(block)
    insertPt = rs.BlockInstanceInsertPoint(block)
    objs = rs.ExplodeBlockInstance(block, False)
    rs.TransformObjects(objs, rs.XformInverse(xform))
    pt = rs.TransformObject(insertPt, rs.XformInverse(xform))
    rs.AddBlock(objs, insertPt, newName, True)
    newBlock = rs.InsertBlock2(newName, xform)
    rs.DeleteObject(pt)
    return newBlock

def MakeBlockUniqueButton():
    try:
        block = rs.GetObject("Select block to make unique", rs.filter.instance, preselect = True)
        if block is None: return

        defaultName = utils.UpdateString(rs.BlockInstanceName(block))

        looping = True
        while looping:
            newName = rs.StringBox("Enter new block name", default_value = defaultName, title = 'MakeUnique')
            if newName is None: return
            if rs.IsBlock(newName):
                print "Block name already exists"
            elif len(newName) == 0:
                print "Must specify a name"
            else:
                looping = False

        if newName is None: return

        rs.EnableRedraw(False)
        newBlock = MakeBlockUnique(block, newName)
        rs.EnableRedraw(True)
        rs.SelectObject(newBlock)
        return True
    except:
        return False

##############################################################################
#Iterate Design Option
def ReplicateBlock(blockObj):
    #Copy block
    copiedBlock = rs.CopyObject(blockObj)

    #Get new block name
    origName = rs.BlockInstanceName(blockObj)
    defaultName = origName
    for i in range(100):
        defaultName = utils.UpdateString(defaultName)
        if origName == defaultName:
            break
        if rs.IsBlock(defaultName) == False:
            break
    
    looping = True
    while looping:
        newBlockName = rs.StringBox("Enter new block name", default_value = defaultName, title = 'Iterate Design Option')
        if newBlockName is None:
            rs.DeleteObject(copiedBlock)
            return
        if rs.IsBlock(newBlockName):
            print "Block name already exists"
        elif len(newBlockName) == 0:
            print "Must specify a name"
        else:
            looping = False


    if newBlockName is None:
        rs.DeleteObject(copiedBlock)
        return

    #Get previous base point
    xform = rs.BlockInstanceXform(copiedBlock)
    basePoint = rs.BlockInstanceInsertPoint(copiedBlock)

    #Explode block
    objsInside = rs.ExplodeBlockInstance(copiedBlock)

    rs.AddBlock(objsInside, basePoint, newBlockName, True)
    #Create new block
    instance = rs.InsertBlock2(newBlockName, xform)
    return instance

def Iterate():
    block = rs.GetObject("Select Design Option Block to iterate", rs.filter.instance, True)
    if block is None: return

    try:
        prevBlockName = rs.BlockInstanceName(block)
        prevBlockLayer = rs.ObjectLayer(block)
        prevBlockLayerColor = rs.LayerColor(prevBlockLayer)
        
        
        newBlock = ReplicateBlock(block)
        newBlockName = rs.BlockInstanceName(newBlock)
        
        #Ensure 3_DESIGN OPTIONS already exists
        parentLayer = layers.AddLayerByNumber(3000, False)[0]
        rs.LayerVisible(parentLayer, True)
        
        #Create new design option layer
        #newBlockLayer = rs.AddLayer(parentLayer + "::" + newBlockName, color = utils.StepColor(prevBlockLayerColor))
        newBlockLayer = rs.AddLayer(parentLayer + "::" + newBlockName, color = utils.GetRandomColor())
        rs.ObjectLayer(newBlock, newBlockLayer)
        
        #Save user text
        try:
            parentsUserTest = rs.GetUserText(block, 'Design Option History') + "<--"
        except:
            parentsUserTest = ''
        rs.SetUserText(newBlock, 'Design Option History',parentsUserTest + newBlockName)
        
        #Turn off prev blocks layer
        if rs.CurrentLayer() != prevBlockLayer:
            rs.LayerVisible(prevBlockLayer, False)
        
        result = True
    except:
        result = False
        newBlockName = ''
    utils.SaveFunctionData('Blocks-Iterate', [__version__, rs.BlockInstanceName(block), newBlockName, result])
    return result

def ResetBlockScale():
    try:
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
        return True
    except:
        return False

##############################################################################
#Design History
def DesignHistory():
    print "Design Option History"
    block = rs.GetObject("Select Design Option Block", rs.filter.instance, preselect = True)
    history = rs.GetUserText(block, 'Design Option History')
    names = history.split("<--")
    message = ''
    for i in range(len(names)):
        message+=names[i]
        if i != len(names)-1:
            message+= '\n' + ('\t'*(i+1)) + '|——'
    
    print message
    #rs.MessageBox(message, 0, 'Design History')

###############################################################################
def ExportAndLinkBlock():
    try:
        name = rs.ListBox(rs.BlockNames(True), 'Select Block to Export and Link', 'Export and Link')
        if name is None: return

        path = rs.SaveFileName('Export and Link', "Rhino 6 3D Models|.3dm||", filename = name)
        if path is None: return

        try:
            rs.Command("_-BlockManager e " + '"' + name + '" ' + path + ' Enter', False)
            rs.Command("_-BlockManager _Properties " + '"' + name + '"' + " _UpdateType i " + path + " _UpdateType _Linked _Enter _Enter", False)
        except:
            pass
        return True
    except:
        return False

###############################################################################
#Create Design Option
def CreateDesignOption():
    objs = rs.GetObjects("Select objects to create design option with", preselect = True)
    if objs is None: return None
    try:
        date = utils.GetDatePrefix()
        origName = date + '_OPTION_00'
        defaultName = origName
        for i in range(100):
            defaultName = utils.UpdateString(defaultName)
            if origName == defaultName:
                break
            if rs.IsBlock(defaultName) == False:
                break
        
        
        
        looping  = True
        while looping:
            designOptionName = rs.StringBox("Design Option Name", defaultName, "Create Design Option")
            if designOptionName is None: return None
            if rs.IsBlock(designOptionName):
                print "Block name already exists"
            elif len(designOptionName) == 0:
                print "Must specify a name"
            else:
                looping = False
        block = rs.AddBlock(objs, (0,0,0), designOptionName, True)
        blockInstance = rs.InsertBlock(designOptionName, (0,0,0))
        
        #Add user text
        rs.SetUserText(blockInstance, 'Design Option History', designOptionName)
        
        #Ensure 3_DESIGN OPTIONS already exists
        layers.AddLayerByNumber(3000, False)
        
        #Create new layer
        parentLayer = layers.GetLayerNameByNumber(3000)
        designOptionLayer = rs.AddLayer(parentLayer + "::" + designOptionName, color = utils.GetRandomColor())
        rs.ObjectLayer(blockInstance, designOptionLayer)
        utils.SaveFunctionData('Blocks-Create Design Option', [__version__, designOptionName])
        return True
    except:
        print "Failed to create design option"
        utils.SaveFunctionData('Blocks-Create Design Option', [__version__, '', 'Failed'])
        return None


if __name__ == "__main__":
    func = rs.GetInteger("", 0, 0, 100)
    if func == 0:
        result = Iterate()
        if result:
            utils.SaveToAnalytics('blocks-iterate')
    elif func == 1:
        result = MakeBlockUniqueButton()
        if result:
            utils.SaveToAnalytics('blocks-Make Unique')
    elif func == 2:
        result = SuperExplodeBlock()
        if result is not None:
            utils.SaveToAnalytics('blocks-Super Explode')
    elif func == 3:
        result = RenameBlockButton()
        if result is not None:
            utils.SaveToAnalytics('blocks-Rename Block')
    elif func == 4:
        result = ResetBlockScale()
        if result:
            utils.SaveToAnalytics('blocks-Reset Block Scale')
    elif func == 5:
        result = ExportAndLinkBlock()
        if result:
            utils.SaveToAnalytics('blocks-Export and Link Block')
    elif func == 6:
        result = CreateDesignOption()
        if result:
            utils.SaveToAnalytics('blocks-Create Design Option')
    elif func == 7:
        result = DesignHistory()
        if result:
            utils.SaveToAnalytics('blocks-Design History')
    else:
        print "No function found"
