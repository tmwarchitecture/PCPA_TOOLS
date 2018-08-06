import rhinoscriptsyntax as rs
import utils
import subprocess
import config

__author__ = 'Tim Williams'
__version__ = "2.0.1"

def OpenFolder(path):
    try:
        subprocess.call("explorer " + path, shell=True)
        return True
    except:
        return False

if __name__ == "__main__":
    func = rs.GetInteger("Func number")
    fileLocations = config.GetDict()

    if func == 0:
        OpenFolder(fileLocations['PCPA GH Components'])
    if func == 1:
        OpenFolder(fileLocations['GH Dependencies'])
    if func == 2:
        OpenFolder(fileLocations['Template Folder'])
    if func == 3:
        OpenFolder(fileLocations['Display Mode Folder'])
    if func == 4:
        OpenFolder(fileLocations['ACAD Scheme Folder'])
