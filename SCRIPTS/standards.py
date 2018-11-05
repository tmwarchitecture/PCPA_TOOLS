import shutil
import distutils.dir_util
import os
import rhinoscriptsyntax as rs
import stat

import config
import utils

__author__ = 'Tim Williams'
__version__ = "2.1.0"

def PreloadCheck():
    if rs.ExeVersion() < 6:
        print "***Reload standards only works for Rhino 6***"
        rs.MessageBox('Reload standards only works for Rhino 6', 0, 'Reload Standards')
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
        result = True
        utils.SaveToAnalytics('standards-Load Materials')
    except:
        print "Failed to load PCPA Materials"
        result = False
    utils.SaveFunctionData('Standards-Load Materials', [result])

#NOT WORKING - Folder set to read-only
def LoadPSSwatch(PSswatch, PSdir):
    print PSswatch
    if os.path.isfile(PSswatch):
        print "File exists"
    else:
        print "Could not find the PCPA Swatch"
        return None

    if os.path.isdir(PSdir):
        print "Photoshop Installation found"
    else:
        print "Could not find your photoshop installation"
        return None

    #os.chmod(PSdir, stat.S_IWRITE )
    #shutil.copy2(PSswatch, PSdir)

    #print PSdir
    print "Loaded PS Swatch"

def ApplyPCPAAliases(scriptFolder):
    try:
        ############################################################################
        #ARCHITECTURE
        
        #STAIR
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\stair.py) '
        rs.AddAlias('pcpStair', str)
        
        #RAMP
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\ramp.py) '
        rs.AddAlias('pcpRamp', str)
    
        ############################################################################
        #BLOCKS
        
        #ITERATE DESIGN OPTION
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\blocks.py) 0 '
        rs.AddAlias('pcpIterDesignOpt', str)
        
        #MAKE BLOCK UNIQUE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\blocks.py) 1 '
        rs.AddAlias('pcpMakeUnique', str)
        
        #SUPER EXPLODE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\blocks.py) 2 '
        rs.AddAlias('pcpSuperExplode', str)
        
        #POPULATE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\populate.py) '
        rs.AddAlias('pcpPopulate', str)
        
        #RESET BLOCK SCALE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\blocks.py) 4 '
        rs.AddAlias('pcpResetBlockScale', str)
        
        #EXPORT AND LINK
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\blocks.py) 5 '
        rs.AddAlias('pcpExportAndLink', str)
    
        ############################################################################
        #DRAWINGS
        
        #AREA TAG
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\drawing.py) 0 '
        rs.AddAlias('pcpAreaTag', str)
        
        #DIM PLINE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\drawing.py) 1 '
        rs.AddAlias('pcpDimPline', str)
        
        #ADD LAYOUT
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\layout.py) 0 '
        rs.AddAlias('pcpLayout', str)
        
        #CUT MODEL
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\cut_model.py)  '
        rs.AddAlias('pcpCutModel', str)
    
        ############################################################################
        #GEOMETRY
        
        #CONTOUR AT POINT
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\geometry.py) 0 ) '
        rs.AddAlias('pcpContourPt', str)
    
        #UNFILLET
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\geometry.py) 1 '
        rs.AddAlias('pcpUnfillet', str)
    
        #RECTIFY
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\rectify.py) '
        rs.AddAlias('pcpRectify', str)
    
        ############################################################################
        #COLOR
        
        #COLOR RANDOM RANGE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\colors.py) 1 '
        rs.AddAlias('pcpColorRandRange', str)
    
        #COLOR GRADIENT
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\colors.py) 0 '
        rs.AddAlias('pcpColorGradient', str)
    
        #COLOR BY SIZE
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\colors.py) 3 '
        rs.AddAlias('pcpColorBySize', str)
    
        #COLOR TO MATERIAL
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\colors.py) 2 '
        rs.AddAlias('pcpColorToMaterial', str)
    
        ############################################################################
        #I/O
        
        #CAPTURE DISPLAY MODES
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\file_IO.py) 3 '
        rs.AddAlias('pcpCaptureDisplayModes', str)
        
        #EXPORT TO RENDER DWG
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\file_IO.py) 1 '
        rs.AddAlias('pcpExportToRenderDWG', str)
        
        #EXPORT TO RENDER SKP
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\file_IO.py) 2 '
        rs.AddAlias('pcpExportToRenderSKP', str)
        
        #IMPORT CAD
        str = r'_NoEcho -_RunPythonScript ('+ scriptFolder +'\\file_IO.py) 0 '
        rs.AddAlias('pcpImportCAD', str)
        print "\tLoaded PCPA Aliases"
        result = True
    except:
        print "Failed to load PCPA Aliases"
        result = False
    utils.SaveFunctionData('Standards-Load PCPA Aliases', [__version__, result])
    return result

################################################################################

def UpdateFolders(sourceMain, targetRoot):
    #Get new folder names
    PCPAroot = os.path.basename(os.path.normpath(sourceMain))
    targetMain = os.path.join(targetRoot, PCPAroot)
    
    #Remove Previous Version
    oldPath = os.path.join(targetRoot, r'00_PCPA Standard Set')
    if os.path.isdir(oldPath):
        print "Contains old version"
        os.chmod(oldPath, stat.S_IWRITE)
        shutil.rmtree(oldPath)

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
                print "\tLoaded {} GH Components".format(targetSubShort)
            except:
                print "\tFailed to load PCPA {} GH Components".format(targetSubShort)
        else:
            extension = os.path.splitext(sourceSub)[1]
            if extension == '.ghuser' or extension == '.ghpy':
                try:
                    shutil.copy2(sourceSub, targetMain)
                    print "\tUpdated PCPA {}".format(os.path.splitext(os.path.basename(sourceSub))[0])
                except:
                    print "\tFailed to load PCPA {} GH Component".format(targetSubShort)
    return len(targetSubsShort)

def LoadPCPAComponents(sourceFolder):
    """
    copies PCPA GH Toolbar from source folder to the grasshopper UserObject folder
    """
    if os.path.isdir(sourceFolder) is False:
        print "FAIL-----PCPA Components folder not found"
        result = False
    try:
        appData = os.getenv('APPDATA')
        targetFolder = appData + r"\Grasshopper\UserObjects"
    except:
        print "FAIL-----UserObjects folder not found"
        result = False
    numberOfObjects = 0
    try:
        numberOfObjects = UpdateFolders(sourceFolder, targetFolder)
        result = True
    except:
        print "FAIL-----Could not copy files. Ensure that folder is not open"
        result = False
    utils.SaveFunctionData('Standards-PCPA GH Components', [numberOfObjects, result])

def LoadGHDependencies(fileLocations):
    """
    copies GH Dependencies from source folder to the grasshopper library folder
    """
    sourceFolderLibraries = fileLocations['GH Dependencies_Libraries']
    sourceFolderUserObjects = fileLocations['GH Dependencies_User Objects']
    
    if os.path.isdir(sourceFolderLibraries) is False:
        print "FAIL-----'GH Dependecies Libraries' folder not found"
        result = False
    if os.path.isdir(sourceFolderUserObjects) is False:
        print "FAIL-----'GH Dependecies UserObjects' folder not found"
        result = False

    try:
        appData = os.getenv('APPDATA')
        targetFolderLibraries = appData + r"\Grasshopper\Libraries"
        targetFolderUserObjects = appData + r"\Grasshopper\UserObjects"
        result = True
    except:
        print "FAIL-----GH Library or User Object folder not found"
        result = False
    numberOfLibraryObjects = 0
    numberOfUserObjects = 0
    try:
        numberOfLibraryObjects = UpdateFolders(sourceFolderLibraries, targetFolderLibraries)
        numberOfUserObjects = UpdateFolders(sourceFolderUserObjects, targetFolderUserObjects)
        result = True
    except:
        print "FAIL-----Could not copy dependencies. You must have Grasshopper open. Close and reopen Rhino, then run this again."
        result = False

    utils.SaveFunctionData('Standards-PCPA GH Dependencies', [numberOfLibraryObjects, numberOfUserObjects, result])

if __name__ == "__main__":
    PreloadCheck()

    standardsRequested = rs.GetInteger("Standards to import", number = 0, minimum = 0, maximum = 10000)
    fileLocations = config.GetDict()
    if standardsRequested == 0:
        LoadPCPAMaterials(fileLocations['Material File'])
    elif standardsRequested == 1:
        SetTemplateFolder(fileLocations['Template Folder'])
        SetTemplateFile(fileLocations['Template File'])
        utils.SaveToAnalytics('standards-Set Template')
    elif standardsRequested == 2:
        LoadPCPAComponents(fileLocations['PCPA GH Components'])
        LoadGHDependencies(fileLocations)
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
    elif standardsRequested == 6:
        LoadPSSwatch(fileLocations['PS Swatch File'], fileLocations['PS Directory'])
        utils.SaveToAnalytics('standards-Load PS Swatch')
    elif standardsRequested == 7:
        result = ApplyPCPAAliases(fileLocations['Scripts Folder'])
        if result: utils.SaveToAnalytics('Standards-Load PCPA Aliases')
    elif standardsRequested == 99:
        LoadPCPAMaterials(fileLocations['Material File'])
        SetTemplateFolder(fileLocations['Template Folder'])
        SetTemplateFile(fileLocations['Template File'])
        LoadDisplayModes(fileLocations['Display Mode Folder'])
        LoadStyles(fileLocations['Template File'])
        LoadAcadSchemes(fileLocations['ACAD Scheme Folder'])
        LoadPCPAComponents(fileLocations['PCPA GH Components'])
        LoadGHDependencies(fileLocations)
        ApplyPCPAAliases(fileLocations['Scripts Folder'])
        utils.SaveToAnalytics('Standards-All')
    else:
        pass
