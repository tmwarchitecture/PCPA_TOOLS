import utils

__author__ = 'Tim Williams'
__version__ = "2.0.1"

def GetDict():
    fileLocationsPCPNY = {
    'Template File' : r'X:\05_RHINO STANDARDS\11 PCPA TEMPLATE\CURRENT\PCPA_Template.3dm',
    'Template Folder' : r'X:\05_RHINO STANDARDS\11 PCPA TEMPLATE\CURRENT',
    'ACAD Scheme Folder' : r'X:\05_RHINO STANDARDS\00 GENERAL SETTINGS\ACAD_Schemes',
    'Display Mode Folder' : r'X:\05_RHINO STANDARDS\02 DISPLAY MODES\2018 PCPA Display Modes',
    'Analytics' : r'X:\22_REACH\03 TOOLS\PCPA_RHINO_TOOLBAR\data\raw\Analytics.csv',
    'Data Folder' : r'X:\22_REACH\03 TOOLS\PCPA_RHINO_TOOLBAR\data\raw',
    'PCPA Layers' : r'X:\22_REACH\03 TOOLS\PCPA_RHINO_TOOLBAR\13 PCPA LAYERS\2.1\PCPA_Layers.csv',
    'PCPA Layers_V1' : r'X:\05_RHINO STANDARDS\13 PCPA LAYERS\1.0\PCPA LAYERS_V1.csv',
    'CSV' : r'X:\22_REACH\03 TOOLS\PCPA_RHINO_TOOLBAR\SCRIPTS\libs\csv.py',
    'PCPA GH Components' : r'X:\22_REACH\03 TOOLS\PCPA_GH_TOOLBAR\CURRENT',
    'GH Dependencies' : r'X:\05_RHINO STANDARDS\04 GRASSHOPPER\00_PCPA Standard Set',
    'Material File' : r'X:\05_RHINO STANDARDS\01 MATERIALS\PCPA_Materials.3dm',
    'Material Folder' : r'X:\05_RHINO STANDARDS\01 MATERIALS',
    'People 3D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\01_PEOPLE\3D',
    'People 2D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\01_PEOPLE\2D',
    'Vegetation 2D Folder' : r'X:\05_RHINO STANDARDS\08 BLOCKS\02_VEGETATION\2D',
    'Help File' : r'X:\05_RHINO STANDARDS\10 PCPA RHINO MANUAL\CURRENT\PCPA Rhino Tools Manual.pdf',
    'PCPA Logo' : r'X:\05_RHINO STANDARDS\01 PCPA TOOLS\TOOLBAR\DEV\ICONS\PCPA_LOGO.png',
    'PS Swatch File' : r'X:\08_ADOBE + OTHER SOFTWARE\01_PHOTOSHOP\PCPA Swatch Library\PCPA.aco',
    'PS Directory' : r'C:\Program Files\Adobe\Adobe Photoshop CS6 (64 Bit)\Presets\Color Swatches'
    }

    fileLocationsPCPNH = {
    'Template File' : r'D:\PCPA_Toobar_local\PCPA_TOOLS_dup\RHINO TEMPLATE\0.2\PCPA_TEMPLATE.3dm',
    'Template Folder' : r'D:\PCPA_Toobar_local\PCPA_TOOLS_dup\RHINO TEMPLATE\0.2',
    'ACAD Scheme Folder' : r'',
    'Display Mode Folder' : r'',
    'Analytics' : r'D:\PCPA_TOOLS\SCRIPTS\data\Analytics.csv',
    'PCPA Layers' : r'D:\PCPA_TOOLS\SCRIPTS\data\PCPA LAYERS_V2.csv',
    'PCPA Layers_V1' : r'D:\PCPA_TOOLS\SCRIPTS\data\PCPA LAYERS_V1.csv',
    'CSV' : r'D:\PCPA_TOOLS\SCRIPTS\libs\csv.py',
    'PCPA GH Components' : r'D:\PCPA_TOOLS\GH\PCPA_GH_TOOLBAR',
    'GH Dependencies' : r'D:\REACHCampus\00_PCPA Standard Set',
    'Material File' : r'',
    'Material Folder' : r'',
    'People 3D Folder' : r'',
    'People 2D Folder' : r'',
    'Vegetation 2D Folder' : r'',
    'Help File' : r'',
    'PCPA Logo' : r'D:\PCPA_TOOLS\RHINO TEMPLATE\0.2\PCPA_TEMPLATE_embedded_files\PCPA_LOGO.png'
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
