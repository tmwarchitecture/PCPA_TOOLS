import rhinoscriptsyntax as rs
import utils
import subprocess
import config


def launchHelp():
    try:
        fileLocations = config.GetDict()
        path = fileLocations['Help File']
        subprocess.Popen([path],shell=True)
        return True
    except:
        return False

if __name__ == "__main__":
    if launchHelp():
        utils.SaveToAnalytics('Help')