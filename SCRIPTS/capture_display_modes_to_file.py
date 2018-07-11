import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import os
import utils

def exportImage(path, name, width, height):
    try:
        shortName = os.path.splitext(path)[0]
        fullName = shortName + '_' + name + '.png'
        comm=' -_ViewCaptureToFile '  + ' _Width=' + str(width) + ' _Height=' + str(height) + ' _Scale=1 _DrawGrid=_No _DrawWorldAxes=_No _DrawCPlaneAxes=_No _TransparentBackground=_Yes ' + '"' + fullName + '"'+ ' _Enter'
        rs.Command(comm,False)
    except:
        pass

def CaptureDisplayModesToFile():
    
    displayModeNames = []
    displayModeBool = []
    displayModesChecked = []
    
    for each in Rhino.Display.DisplayModeDescription.GetDisplayModes():
        displayModeNames.append(each.EnglishName)
        if each.EnglishName[:4] == 'PCPA':
            displayModeBool.append(True)
        else:
            displayModeBool.append(False)
    
    results = rs.CheckListBox(zip(displayModeNames, displayModeBool), 'Select Display Modes', 'Capture Display Modes To File')
    if results is None: return
    for each in results:
        if each[1]:
            displayModesChecked.append(each[0])
    
    date = utils.GetDatePrefix()
    if date is None: date = 'DATE'
    activeView = sc.doc.Views.ActiveView.ActiveViewport.Name
    if activeView is None: activeView = 'VIEW'
    path = rs.SaveFileName('Export All Display Modes', "PNG (*.png)|*.png||", filename = date+'_'+activeView)
    if path is None: return
    
    if 'catpureDisplays-width' in sc.sticky:
        widthDefault = sc.sticky['catpureDisplays-width']
    else:
        widthDefault = 3060
    
    if 'catpureDisplays-height' in sc.sticky:
        heightDefault = sc.sticky['catpureDisplays-height']
    else:
        heightDefault = 1980
    
    width = rs.GetInteger('Image Width', number = widthDefault, minimum = 600, maximum = 20000)
    height = rs.GetInteger('Image Height', number = heightDefault, minimum = 600, maximum = 20000)
    
    sc.sticky['catpureDisplays-width'] = width
    sc.sticky['catpureDisplays-height'] = height
    
    
    for name in displayModesChecked:
        try:
            rs.Command('-_SetDisplayMode m ' +  name  + ' Enter', False)
            exportImage(path, name, width, height)
        except:
            pass

if __name__ == "__main__":
    CaptureDisplayModesToFile()
