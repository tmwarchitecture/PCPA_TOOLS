import os


def GetNetworkLocation():
    NYPath = r'X:' # index = 0
    NHPath = r'H:' # index = 1
    
    if os.path.isdir(NYPath):
        location = "New York"
    elif os.path.isdir(NHPath):
        location = "New Haven"
    else:
        print "Could not find NY or NH network"
        return 
    return "You are connected to the {} network.".format(location)

def CreatePCPAFolder():
    appData = os.getenv('APPDATA')
    folder = os.path.join(appData, 'PCPA')
    
    if os.path.isdir(folder):
        print "Exists already"
    else:
        os.makedirs(folder)

if __name__ == "__main__":
    CreatePCPAFolder()
    print GetNetworkLocation()