fileLocationsPCPNY = {
'Template File' : r'X:\05_RHINO STANDARDS\PCPA.3dm',
'Template Folder' : r'X:\05_RHINO STANDARDS',
'ACAD Scheme Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\ACAD_Schemes',
'Display Mode Folder' : r'X:\05_RHINO STANDARDS\02 DISPLAY SETTINGS\2018 Display Modes',
'Analytics' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\data\Analytics.csv',
'FunctionCounter.py' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON',
'PCPA_Layers' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\data\PCPA LAYERS.csv',
'CSV' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\libs\csv.py',
'PCPA GH Components' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\GH\PCPA_GH_TOOLBAR',
'GH Dependencies' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\03_Install+Plugins\00_PCPA Standard Set',
'Material File' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\PCPA Rhino Materials\PCPA_Materials.3dm'
}

def GetDict():
    return fileLocationsPCPNY

def GetValue(key):
    return fileLocationsPCPNY [key]
