import shutil
import distutils.dir_util
import os
import sys
print sys.version
import rhinoscriptsyntax as rs
import stat
#sys.path.append(r'E:\Files\Work\LIBRARY\06_RHINO\41_PCPA')
sys.path.append(r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA')
import PCPA
fileLocations = PCPA.config.GetDict()

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
    #CheckPaths()
    print "Loading PCPA Standards"

    SetTemplateFolder(fileLocations['Template Folder'])

    SetTemplateFile(fileLocations['Template File'])

    print "\tImport Annotation Styles Broken"
    #UpdateStyles(fileLocations['Template File'])
    
    #print "\tACAD Schemes Broken"
    LoadAcadSchemes(fileLocations['ACAD Scheme Folder']) #GOOD
    
    print "\tDisplay Modes Broken"
    #LoadDisplayModes(fileLocations['Display Mode Folder'])
    
    LoadPCPAComponents(fileLocations['PCPA GH Components'])
    
    LoadGHDependencies(fileLocations['GH Dependencies'])
    print "Reload complete"

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
        UpdateFolders(sourceFolder, targetFolder)
    except:
        print "FAIL-----Could not copy files"
        return None

def LoadGHDependencies(sourceFolder):
    """
    copies GH Dependencies from source folder to the grasshopper library folder
    """
    if os.path.isdir(sourceFolder) is False:
        print "FAIL-----GH Dependecies folder does not exist"
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
        print "FAIL-----Could not copy dependencies"
        return None

if __name__ == "__main__":
    ReloadPCPAStandards()
    #fc.IterateCounter()