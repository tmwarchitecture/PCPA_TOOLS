import rhinoscriptsyntax as rs
import utils
#import subprocess

def launchHelp():
    #PDF METHOD
    #path = r'C:\Users\twilliams\Desktop\TEMP\temp.pdf'
    #subprocess.Popen([path],shell=True)
    
    try:
        path = r'"https://github.com/tmwarchitecture/PCPA_TOOLS/wiki/Rhino-Toolbar"'
        rs.Command('-_WebBrowser n ' + path + ' Enter ', False)
        return True
    except:
        return False

if __name__ == "__main__":
    if launchHelp():
        utils.SaveToAnalytics('Help')