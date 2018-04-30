import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
#The inputs to this node will be stored as a list in the IN variables.
dataEnteringNode = IN[0]

#Assign your output to the OUT variable.

import sys

sys.path.append(r'E:\Files\Work\LIBRARY\06_RHINO\42_PCPA\PCPA\libs')
sys.path.append(r'H:\Program Files\Rhino 6\Plug-ins\IronPython\Lib')

#READ DATA
fileLoc = r'E:\Files\Work\LIBRARY\06_RHINO\42_PCPA\PCPA\examples\Project_Info.yaml'

import yaml

with open(dataEnteringNode, 'r') as fileDescriptor:
    data = yaml.load(fileDescriptor)

client_Name = data.get('Project').get('Client').get('Name')
project_Name = data.get('Project').get('Name')
project_Number = data.get('Project').get('Number')

dataList = [client_Name,project_Name, project_Number ]

OUT = dataList
