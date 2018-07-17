import shutil
import distutils.dir_util
import os
import rhinoscriptsyntax as rs
import stat

import config
import utils

def CheckPaths():
    print "Checking paths"
    keys = list(fileLocations.keys())
    print keys
    for each in keys:
        if (os.path.exists(fileLocations[each])):
            print "Path exists"
        else:print "Path not found"

def PreloadCheck():
    if rs.ExeVersion() < 6:
        print "***Reload standards only works for Rhino 6***"
        return None

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

def LoadStyles(filepath = None):
    if filepath is None:
        fileLocations = config.GetDict()
        filepath = '"' + fileLocations['Template File'] + '"'
    else:
        filepath = '"' + filepath + '"'
    
    try:
        rs.Command('-_ImportAnnotationStyles ' + filepath + ' Enter Enter Enter', echo=False)
        print "\tAnnotation Styles Updated"
    except:
        print "FAIL-----Annotation Style Import Failed"

def LoadAcadSchemes(filepath):
    if os.path.isdir(filepath) is False:
        print "FAIL-----ACAD Scheme folder not found"
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
        print "FAIL-----Display Mode folder not found"
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
        print "\tNo display modes updated"
    elif len(allFiles)==1:
        print "\t{} Display mode updated".format(len(allFiles))
    else:
        print "\t{} Display modes updated".format(len(allFiles))

def LoadPCPAMaterials(filepath):
    try:
        rs.EnableRedraw(False)
        rs.Command("-_Import " + '"' + filepath + '"  Enter' , echo = False)
        rs.EnableRedraw(True)
    except:
        print "Failed to load PCPA Materials"

def UpdateFolders(sourceMain, targetRoot):
    #Get new folder names
    PCPAroot = os.path.basename(os.path.normpath(sourceMain))
    targetMain = os.path.join(targetRoot, PCPAroot)
    #Ensure targetMain exists
    if os.path.isdir(targetMain):
        os.chmod(targetMain, stat.S_IWRITE)
        #print "Changed mode"
        shutil.rmtree(targetMain)
        #print "removed tree"
        os.makedirs(targetMain)
        #print "made new tree"
    else:
        os.makedirs(targetMain)
    #Create subfolders
    targetSubsShort = os.listdir(sourceMain)
    for targetSubShort in targetSubsShort:
        sourceSub = os.path.join(sourceMain, targetSubShort)
        if os.path.isdir(sourceSub):
            #print "{} is a directory".format(sourceSub)
            try:
                targetSub = os.path.join(targetMain, targetSubShort)
                os.makedirs(targetSub)
                distutils.dir_util.copy_tree(sourceSub, targetSub)
                print "\tLoaded PCPA {} GH Components".format(targetSubShort)
            except:
                print "\tFailed to load PCPA {} GH Components".format(targetSubShort)

def LoadPCPAComponents(sourceFolder):
    """
    copies PCPA GH Toolbar from source folder to the grasshopper UserObject folder
    """
    if os.path.isdir(sourceFolder) is False:
        print "FAIL-----PCPA Components folder not found"
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
        UpdateFolders(sourceFolder, targetFolder)
    except:
        print "FAIL-----Could not copy files"
        return None

def LoadGHDependencies(sourceFolder):
    """
    copies GH Dependencies from source folder to the grasshopper library folder
    """
    if os.path.isdir(sourceFolder) is False:
        print "FAIL-----GH Dependecies folder not found"
        return None
    else:
        allFiles = os.listdir(sourceFolder)
    
    try:
        appData = os.getenv('APPDATA')
        targetFolder = appData + r"\Grasshopper\Libraries"
    except:
        print "FAIL-----GH Library folder not found"
        return None
    
    try:
        UpdateFolders(sourceFolder, targetFolder)
    except:
        print "FAIL-----Could not copy dependencies. You must have grasshopper open. Close and reopen Rhino, then run this again."
        return None

if __name__ == "__main__":
    PreloadCheck()
    
    standardsRequested = rs.GetInteger("Standards to import", number = 0, minimum = 0, maximum = 10000)
    fileLocations = config.GetDict()
    if standardsRequested == 0:
        LoadPCPAMaterials(fileLocations['Material File'])
        utils.SaveToAnalytics('standards-Load Materials')
    elif standardsRequested == 1:
        SetTemplateFolder(fileLocations['Template Folder'])
        SetTemplateFile(fileLocations['Template File'])
        utils.SaveToAnalytics('standards-Set Template')
    elif standardsRequested == 2:
        LoadPCPAComponents(fileLocations['PCPA GH Components'])
        LoadGHDependencies(fileLocations['GH Dependencies'])
        utils.SaveToAnalytics('standards-Load GH Components')
    elif standardsRequested == 3:
        LoadAcadSchemes(fileLocations['ACAD Scheme Folder'])
        utils.SaveToAnalytics('standards-Load ACADSchemes')
    elif standardsRequested == 4:
        LoadStyles(fileLocations['Template File'])
        utils.SaveToAnalytics('standards-Load Styles')
    elif standardsRequested == 5:
        LoadDisplayModes(fileLocations['Display Mode Folder'])
        utils.SaveToAnalytics('standards-Load Display Modes')
    elif standardsRequested == 99:
        LoadPCPAMaterials(fileLocations['Material File'])
        SetTemplateFolder(fileLocations['Template Folder'])
        SetTemplateFile(fileLocations['Template File'])
        LoadDisplayModes(fileLocations['Display Mode Folder'])
        LoadStyles(fileLocations['Template File'])
        LoadAcadSchemes(fileLocations['ACAD Scheme Folder'])
        LoadPCPAComponents(fileLocations['PCPA GH Components'])
        LoadGHDependencies(fileLocations['GH Dependencies'])
        utils.SaveToAnalytics('standards-All')
    else:
        pass