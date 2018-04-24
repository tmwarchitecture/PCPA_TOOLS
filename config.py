fileLocationsHOME = {
'Template File' : r'X:\05_RHINO STANDARDS\PCPA.3dm',
'Template Folder' : r'X:\05_RHINO STANDARDS',
'ACAD Scheme Folder' : r'X:\05_RHINO STANDARDS\01 GENERAL SETTINGS\ACAD_Schemes',
'Display Mode Folder' : r'X:\05_RHINO STANDARDS\02 DISPLAY SETTINGS\2018 Display Modes',
'PCPA GH Components' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\03_Install+Plugins\PCPA\V.01.02',
'Analytics' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\Analytics.csv',
'FunctionCounter.py' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON',
'PCPA_Layers' : r'C:\Users\Tim\Desktop\temp\template\PCPA LAYERS.csv',
'CSV' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\dependencies\csv.py'
}

fileLocationsPCPNY = {
'Template File' : r'X:\05_RHINO STANDARDS\PCPA.3dm',
'Template Folder' : r'X:\05_RHINO STANDARDS',
'ACAD Scheme Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\ACAD_Schemes',
'Display Mode Folder' : r'X:\05_RHINO STANDARDS\02 DISPLAY SETTINGS\2018 Display Modes',
'PCPA GH Components' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\03_Install+Plugins\00_PCPA\PCPA_GH_TOOLBAR',
'Analytics' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\data\Analytics.csv',
'FunctionCounter.py' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON',
'PCPA_Layers' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\data\PCPA LAYERS.csv',
'CSV' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\libs\csv.py',
'GH Dependencies' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\03_Install+Plugins\00_PCPA Standard Set',
'Titleblock 8.5x11L' : r'X:\05_RHINO STANDARDS\10 TITLEBLOCKS\PROJ_TBLK 8.5x11L.dwg',
'Titleblock 11x17L' : r'X:\05_RHINO STANDARDS\10 TITLEBLOCKS\PROJ_TBLK 11x17L.dwg',
'Titleblock 18x24L' : r'X:\05_RHINO STANDARDS\10 TITLEBLOCKS\PROJ_TBLK 18x24L.dwg'
}

def GetDict():
    return fileLocationsPCPNY

def GetValue(key):
    return fileLocationsPCPNY [key]
