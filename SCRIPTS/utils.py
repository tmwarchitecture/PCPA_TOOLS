import datetime
import os

def GetDatePrefix():
    year = int(datetime.datetime.today().strftime('%Y'))-2000
    md = datetime.datetime.today().strftime('%m%d')
    return str(year) + str(md)

def GetNetworkLocation():
    NYPath = r'X:'
    NHPath = r'H:'
    
    
    if os.path.isdir(NYPath):
        location = "New York"
    elif os.path.isdir(NHPath):
        location = "New Haven"
    else:
        print "Could not find NY or NH network"
        return 
    return "You are connected to the {} network.".format(location)


if __name__ == "__main__":
    print GetNetworkLocation()