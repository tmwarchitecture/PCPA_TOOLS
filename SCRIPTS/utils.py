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

def SaveFunctionData(funcName, funcData):
    """
    SaveFunctionData(funcName, funcData)
    funcName = name of function(str)
    funcData = data to save [list]
    """
    try:
        filepath = 'data\\' + funcName + '.csv'
        userName = encrypt.encrypt(getpass.getuser())
        now=datetime.datetime.now()
        timeString=('%02d-%02d-%02d_%02d:%02d:%02d.%d'%(now.year, now.month, now.day, now.hour, now.minute,now.second,now.microsecond))[:-4]
        
        
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as File:
                reader = csv.reader(File)
                data = list(reader)
            row = [timeString] + [userName]  + funcData
            data.append(row)
        else:
            data = [[funcName],['Date', 'User']]
        
        
        myFile = open(filepath, 'wb')
        with myFile:
            csvwriter = csv.writer(myFile)
            csvwriter.writerows(data)
    except:
        print "SaveFunctionData failed"

def RoundNumber(number, decPlaces):
    """Rounds numbers and adds ',' thousand seperator. Returns string. -1 rounds to 10, 0 leaves no decimals, 1 has one decimal place"""
    if decPlaces < 0:
        result = int(round(number, decPlaces))
        result = "{:,}".format(result)
    else:
        result = format(float(number), ',.'+str(decPlaces)+'f')
    return result

def RemapList(values, newMin, newMax):
    origMin = min(values)
    origMax = max(values)
    OldRange = (origMax - origMin)  
    NewRange = (newMax - newMin)
    newValues = []
    for value in values:
        newValues.append((((value - origMin  ) * NewRange) / OldRange) + newMin)
    return newValues

if __name__ == "__main__":
    SaveFunctionData('geometry-Test', ['Area', 'Geometry', 42, 'Result', 'Failed'])
    #print GetNetworkLocation()
    #SaveToAnalytics('Count')
    #pass