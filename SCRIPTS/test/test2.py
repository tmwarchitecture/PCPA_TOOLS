import rhinoscriptsyntax as rs
import database_tools as dt


try:
    path = rs.GetDocumentData('PCPA', 'Project_Database')
except:
    print "No level data set"
    path = ''
levelData = dt.GetProjectLevelData(path, 0)

rs.SetDocumentData('PCPA', 'Test', str(levelData))

print rs.GetDocumentData('PCPA', 'Test')