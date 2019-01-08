import rhinoscriptsyntax as rs
import os

def AutoExport(objs):
    appData = os.getenv('APPDATA')
    targetFolder = appData + r"\PCPA\temp.dwg"
    rs.SelectObjects(objs)
    rs.Command('-_Export ' + '"' + targetFolder + '"' + ' s "2007 Natural" Enter ', True)


objs = rs.GetObjects()
AutoExport(objs)