import sys

sys.path.append(r'E:\Files\Work\LIBRARY\06_RHINO\42_PCPA\PCPA\libs')


#READ DATA
fileLoc = r'C:\Users\Tim\Desktop\temp\yaml\test.yaml'
import yaml

with open(fileLoc, 'r') as fileDescriptor:
    data = yaml.load(fileDescriptor)

#print data


#WRITE DATA
data = {
'Version':'0.1', 
'Project':{
    'Name':'The Embankment', 
    'Number':'A1802', 
    'Location':{
        'Street': '2112 Jersey Ave.',
        'City': 'New Jersey',
        'State': 'New Jersey',
        'Country': 'USA'
        },
    'Client':{
        'Name': 'Albanese'
        },
    'Functions': [
        'Residential',
        'Commercial'
        ],
    'Start Date': '2018-04-21'
    },
'Dimensions':{
    'Height': 120
    }
}


data['Project']['Client']['Name'] = 'Test4'

stream = file('Project_Info.yaml', 'w')
yaml.safe_dump(data, stream, default_flow_style=False)
print yaml.safe_dump(data) 
