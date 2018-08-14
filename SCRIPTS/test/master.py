import rhinoscriptsyntax as rs
import os

def GetNetworkLocation():
    """Checks the network to see if X: or H: exist. If X:, then returns 0 (for New York). If H: then returns 1 (for New Haven)
    """
    NYPath = r'X:'
    NHPath = r'H:'


    if os.path.isdir(NYPath):
        location = "New York"
        return 0
    elif os.path.isdir(NHPath):
        location = "New Haven"
        return 1
    else:
        print "Could not find NY or NH network"
        return
    return "You are connected to the {} network.".format(location)

print "MASTER RUNNING"

x = GetNetworkLocation()

if x == 0:
    scriptFolder = r'X:\05_RHINO STANDARDS\12 PCPA TOOLBAR\2.0\scripts'
if x == 1:
    scriptFolder = r'H:\05_RHINO STANDARDS\12 PCPA TOOLBAR\2.0\scripts'


func = rs.GetString()
os.path.join(scriptFolder, func)


print "MASTER DONE"    