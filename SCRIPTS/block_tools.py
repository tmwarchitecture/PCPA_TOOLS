import rhinoscriptsyntax as rs
from pcpa_tools import GetDatePrefix
import layers

def MakeUnique(blockObj):
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

def main():
    block = rs.GetObject("Select block to make unique", rs.filter.instance, True)
    if block is None: return
    newBlock = MakeUnique(block)
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
    main()