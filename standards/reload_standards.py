import rhinoscriptsyntax as rs
import shutil
import os
import sys
sys.path.append(r'E:\Files\Work\LIBRARY\06_RHINO\41_PCPA')
import PCPA
#print dir(PCPA.tools)
fileLocations = PCPA.tools.config.GetDict()

#sys.path.append(fileLocations['FunctionCounter.py'])
#import FunctionCounter as fc

def CheckPaths():
    print "Checking paths"
    keys = list(fileLocations.keys())
    print keys
    for each in keys:
        if (os.path.exists(fileLocations[each])):
            print "Path exists"
        else:print "Path not found"

def ReloadPCPAStandards():
    CheckPaths()
    print "Loading PCPA Standards"
    #SetTemplateFolder(fileLocations['Template Folder'])
    #SetTemplateFile(fileLocations['Template File'])
    #print "\tImport Styles Broken"
    #UpdateStyles(fileLocations['Template File'])
    print "\tACAD Schemes Broken"
    #LoadAcadSchemes(fileLocations['ACAD Scheme Folder']) #GOOD
    print "\tDisplay Modes Broken"
    #LoadDisplayModes(fileLocations['Display Mode Folder'])
    #LoadPCPAComponents(fileLocations['PCPA GH Components'])
    print "File Updated"

def SetTemplateFolder(filepath):
    if os.path.isdir(filepath) is False:
        print "FAIL-----Template Folder"
        return None
    else:
        rs.TemplateFolder(filepath)
        print "\tTemplate Folder Updated"

def SetTemplateFile(filepath):
    try:
        rs.TemplateFile(filepath)
        print "\tTemplate File Updated"
    except:
        print "FAIL-----Template File"

def UpdateStyles(filepath):
    #try:
    #    rs.Command('-_DocumentProperties l l ' + filepath + ' Enter Enter Enter', False)
    #    print "\tLinetypes Updated"
    #except:
    #    print "FAIL-----Linetype Import Failed"
    
    try:
        rs.Command('-_ImportAnnotationStyles ' + filepath + ' Enter Enter Enter', False)
        print "\tAnnotation Styles Updated"
    except:
        print "FAIL-----Annotation Style Import Failed"
    
    #try:
    #    rs.Command('-_ImportAnnotationStyles ' + filepath + ' Enter Enter Enter', False)
    #    print "\tAnnotation Styles Updated"
    #except:
    #    print "FAIL-----Hatch Import Failed"

def LoadAcadSchemes(filepath):
    if os.path.isdir(filepath) is False:
        print "FAIL-----ACAD Scheme folder does not exist"
        return None
    else:
        allFilesRaw = os.listdir(filepath)
    
    allFiles = []
    for file in allFilesRaw:
        if file.endswith(".ini"):
            allFiles.append(file)
    
    if len(allFiles)==0:
        print "\tACAD Schemes not updated. No ACAD Schemes in standards folder"
        return
    
    for file in allFiles:
        fullFilePath = '"' + filepath + '\\' + file + '"'
        shortName = file.split('.')[0]
        rs.Command('-_AcadSchemes i ' + fullFilePath + ' Enter c ' + shortName + ' Enter ', echo=False)
    
    if len(allFiles)==1:
        print "\t{} ACAD Scheme updated".format(len(allFiles))
    else:
        print "\t{} ACAD Schemes updated".format(len(allFiles))

def LoadDisplayModes(filepath):
    if os.path.isdir(filepath) is False:
        print "FAIL-----Display Mode folder does not exist"
        return None
    else:
        allFilesRaw = os.listdir(filepath)
    allFiles = []
    for file in allFilesRaw:
        if file.endswith(".ini"):
            allFiles.append(file)
    
    for file in allFiles:
        fullFilePath = '"' + filepath + '\\' + file + '"'
        rs.Command('-_Options v d i ' + fullFilePath + ' Enter Enter Enter', echo=False)
    
    if len(allFiles)==0:
        print "\tNo files updated"
    elif len(allFiles)==1:
        print "\t{} Display mode updated".format(len(allFiles))
    else:
        print "\t{} Display modes updated".format(len(allFiles))

def LoadPCPAComponents(sourceFolder):
    """
    copies all files from source folder to the grasshopper UserObject folder
    """
    if os.path.isdir(sourceFolder) is False:
        print "FAIL-----PCPA Components folder does not exist"
        return None
    else:
        allFiles = os.listdir(sourceFolder)
    
    try:
        appData = os.getenv('APPDATA')
        targetFolder = appData + r"\Grasshopper\UserObjects"
    except:
        print "FAIL-----UserObjects folder not found"
        return None
    
    try:
        for file in allFiles:
            source = sourceFolder + "\\" + str(file)
            shutil.copytree(source, targetFolder)
    except:
        print "FAIL-----Could not copy files"
        return None
    
    if len(allFiles)==0:
        print "\tNo GH Components updated"
    elif len(allFiles)==1:
        print "\t{} PCPA Grasshopper component updated".format(len(allFiles))
    else:
        print "\t{} PCPA Grasshopper components updated".format(len(allFiles))

if __name__ == "__main__":
    ReloadPCPAStandards()
    #fc.IterateCounter()