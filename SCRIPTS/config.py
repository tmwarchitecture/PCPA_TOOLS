import utils

def GetDict():
    fileLocationsPCPNY = {
    'Template File' : r'X:\05_RHINO STANDARDS\11 PCPA TEMPLATE\CURRENT\PCPA_Template.3dm',
    'Template Folder' : r'X:\05_RHINO STANDARDS\11 PCPA TEMPLATE\CURRENT',
    'ACAD Scheme Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\ACAD_Schemes',
    'Display Mode Folder' : r'X:\05_RHINO STANDARDS\02 DISPLAY SETTINGS\2018 Display Modes',
    'Analytics' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\data\Analytics.csv',
    'PCPA Layers' : r'X:\05_RHINO STANDARDS\13 PCPA LAYERS\CURRENT\PCPA LAYERS_V2.csv',
    'PCPA Layers_V1' : r'X:\05_RHINO STANDARDS\13 PCPA LAYERS\1.0\PCPA LAYERS_V1.csv',
    'CSV' : r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\libs\csv.py',
    'PCPA GH Components' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\GH\PCPA_GH_TOOLBAR',
    'GH Dependencies' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\00_PCPA Standard Set',
    'Material File' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\PCPA Rhino Materials\PCPA_Materials.3dm',
    'Material Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\PCPA Rhino Materials',
    'People 3D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\01_PEOPLE\3D',
    'People 2D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\01_PEOPLE\2D',
    'Vegetation 2D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\02_VEGETATION\2D',
    'Help File' : r'X:\05_RHINO STANDARDS\10 PCPA RHINO MANUAL\PCPA Rhino Tools Manual.pdf',
    'PCPA Logo' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\TOOLBAR\DEV\ICONS\PCPA_LOGO.png'
    }

    fileLocationsPCPNH = {
    'Template File' : r'',
    'Template Folder' : r'',
    'ACAD Scheme Folder' : r'',
    'Display Mode Folder' : r'',
    'Analytics' : r'',
    'PCPA Layers' : r'',
    'CSV' : r'',
    'PCPA GH Components' : r'',
    'GH Dependencies' : r'',
    'Material File' : r'',
    'Material Folder' : r'',
    'People 3D Folder' : r'',
    'People 2D Folder' : r'',
    'Vegetation 2D Folder' : r'',
    'Help File' : r''
    }

    location = utils.GetNetworkLocation()
    if location == 0:
        return fileLocationsPCPNY
    elif location == 1:
        return fileLocationsPCPNH
    else:
        print "Network Location Error"

def GetValue(key):
    print "GetValue Function obsolete"
    return fileLocationsPCPNY [key]

if __name__ == "__main__":
    GetDict()
