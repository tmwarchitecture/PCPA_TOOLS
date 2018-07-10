def GetDict():
    fileLocationsPCPNY = {
    'Template File' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\RHINO TEMPLATE\0.2\PCPA_TEMPLATE.3dm',
    'Template Folder' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\RHINO TEMPLATE\0.2',
    'ACAD Scheme Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\ACAD_Schemes',
    'Display Mode Folder' : r'X:\05_RHINO STANDARDS\02 DISPLAY SETTINGS\2018 Display Modes',
    'Analytics' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\data\Analytics.csv',
    'FunctionCounter.py' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON',
    'PCPA Layers' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\SCRIPTS\data\PCPA LAYERS_V2',
    'CSV' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\libs\csv.py',
    'PCPA GH Components' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\GH\PCPA_GH_TOOLBAR',
    'GH Dependencies' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\03_Install+Plugins\00_PCPA Standard Set',
    'Material File' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\PCPA Rhino Materials\PCPA_Materials.3dm',
    'Material Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\PCPA Rhino Materials',
    'People 3D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\01_PEOPLE\3D',
    'People 2D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\01_PEOPLE\2D',
    'Vegetation 2D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\02_VEGETATION\2D'
    }


    return fileLocationsPCPNY

def GetValue(key):
    print "GetValue Function obsolete"
    return fileLocationsPCPNY [key]
