import datetime
import os
from libs import csv
from libs import encrypt
import getpass


def GetDatePrefix():
    year = int(datetime.datetime.today().strftime('%Y'))-2000
    md = datetime.datetime.today().strftime('%m%d')
    return str(year) + str(md)

def GetNetworkLocation():
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

def SaveToAnalytics(funcName):
    try:
        filepath = 'data\Analytics.csv'
        
        with open(filepath, 'rb') as File:
            reader = csv.reader(File)
            data = list(reader)
        
        #Update date
        data[0][1] = 'Last Updated: ' + GetDatePrefix()
        
        #Username
        userName = encrypt.encrypt(getpass.getuser())
        
        #Update Column
        colPos = None
        for i,item in enumerate(data[1]):
            if item == funcName:
                colPos = i
        if colPos is None:
            colPos = len(data[1])
            data[1].append(funcName)
        
        rowPos = None
        for i,item in enumerate(data):
            if item[0] == userName: 
                rowPos = i
        if rowPos is None:
            rowPos = len(data)
            data.append([userName])
        
        newCells = (colPos+1) - len(data[rowPos])
        for i in range(newCells):
            data[rowPos].append('')
        
        try:
            data[rowPos][colPos] = int(data[rowPos][colPos]) + 1
        except:
            data[rowPos][colPos] = 1
        
        myFile = open(filepath, 'wb')
        with myFile:
            csvwriter = csv.writer(myFile)
            csvwriter.writerows(data)
    except:
        print "Analytics failed"

def RoundNumber(number, decPlaces):
    """Rounds numbers and adds ',' thousand seperator. Returns string. -1 rounds to 10, 0 leaves no decimals, 1 has one decimal place"""
    if decPlaces < 0:
        result = int(round(number, decPlaces))
        result = "{:,}".format(result)
    else:
        result = format(float(number), ',.'+str(decPlaces)+'f')
    return result



if __name__ == "__main__":
    #print GetNetworkLocation()
    #SaveToAnalytics('Count')
    pass