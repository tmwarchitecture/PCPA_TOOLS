import os
import Rhino as rc
import rhinoscriptsyntax as rs
import ast
from libs import yaml

root = os.path.dirname(os.path.realpath(__file__))
yamlPath = os.path.join(root, "data\Database_Template.yaml")

def GetDatabaseTemplate():
    '''
    Gets the yaml databse template
    Input: None
    Returns: Dictionary of yaml file on success
    '''
    try:
        with open(yamlPath, 'r') as fileDescriptor:
            databaseTemplate = yaml.load(fileDescriptor)
        return databaseTemplate
    except:
        return None

def SaveDatabase(data, databaseFile):
    '''
    Saves data from dictionary to a yaml file
    Input:
        data - dictionary
        databaseFile - path to folder to save file
        versionName - Filename for the yaml file
    Returns: "Done" on Success
    '''
    try:
        stream = file(databaseFile, 'w')
        yaml.safe_dump(data, stream, default_flow_style=False)
        return "DONE"
    except:
        return "ERROR SaveDatabase"

def SaveProjectLevelData(data, oldDatabaseFile, newDatabaseFile, bldgNum):
    existingData = GetProjectDatabase(oldDatabaseFile)
    
    
    #print existingData
    
    newDict = {}
    for row in data:
        newDict[row[0]] = {'name': row[1], 'functions': row[2], 'ftf': float(row[3]), 'z': float(row[4]),'area': str(row[5]),'comments': str(row[6]) }
    print newDict
    try:
        existingData['building'][int(bldgNum)]['level'] = newDict
    except:
        existingData = GetDatabaseTemplate()
        existingData['building'][int(bldgNum)]['level'] = newDict
        print "Save failed"
    
    #print newDict
    
    SaveDatabase(existingData, newDatabaseFile)
    print "{} saved".format(newDatabaseFile)

def GetProjectDatabase(databaseFile):
    '''
    Gets the yaml project database
    Input:
        databaseFile - path to the database
    Returns: Dictionary of yaml file on success
    '''
    try:
        with open(databaseFile, 'r') as fileDescriptor:
            databaseTemplate = yaml.load(fileDescriptor)
        return databaseTemplate
    except:
        return None

def GetProjectLevelData(databaseFile, bldgNum):
    data = GetProjectDatabase(yamlPath)
    print "Data: " + str(data)
    levels = []
    try:
        levelData = data['building'][int(bldgNum)]['level']
    except:
        return None
    
    print 'levelData: ' + str(levelData)
    
    for key in levelData.keys():
        levels.append([key, levelData[key]['name'], levelData[key]['functions'], levelData[key]['ftf'], levelData[key]['z'], levelData[key]['area'], levelData[key]['comments']])
    return levels

def LoadLevelsToRhinoDoc(databaseFile):
    print "Loading levels to rhino doc"
    bldgNum = 0
    data = GetProjectLevelData(databaseFile, bldgNum)
    print data
    rs.SetDocumentData('PCPA', 'Levels', str(data))
    return 1

def GetLevelsFromRhinoDoc():
    strLevels = rs.GetDocumentData('PCPA', 'Levels')
    levels = ast.literal_eval(strLevels)
    return levels

def GetLevelsFromAnotherRhinoDoc(filePath):
    try:
        rhinoFile = rc.FileIO.File3dm.Read(filePath)
        strLevels = rhinoFile.Strings.GetValue('PCPA', 'Levels')
        levels = ast.literal_eval(strLevels)
        return levels
    except:
        print "Error: Could not find Project Level data"
        return None

if __name__ == "__main__":
    print GetLevelsFromAnotherRhinoDoc(r'C:\Users\twilliams\Desktop\TEMP\temp3.3dm')
    pass
    #print ""
    
    #data = GetDatabaseTemplate()
    #data['project']['name'] = "TEst"
    #path = r'C:\Users\twilliams\Desktop\TEMP\Database'
    #print SaveDatabase(data, path, 'Project_Info.yaml')
    
    #path = r'C:\Users\twilliams\Desktop\TEMP\Database\MyProject.yaml'
    #GetProjectLevels(path, 'Project_Info.yaml')
    #LoadLevelsToRhinoDoc(path, 0)
    #a = GetLevelsFromRhinoDoc()