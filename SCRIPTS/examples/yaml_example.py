#Read from YAML database
import os
from libs import yaml

root = os.path.dirname(os.path.realpath(__file__))
yamlPath = os.path.join(root, "Project_Info.yaml")

with open(yamlPath, 'r') as fileDescriptor:
    database = yaml.load(fileDescriptor)

print database['Building'][1]['Functions']
print database['Building'][1]['Level'][2]['Name']
print database['Building'][1]['Level'][2]['Z']
print "Number of levels: " + str(len(database['Building'][1]['Level']))


##WRITE DATA
#data = {
#'Version':'0.1', 
#'Project':{
#    'Name':'The Embankment', 
#    'Number':'A1802', 
#    'Location':{
#        'Street': '2112 Jersey Ave.',
#        'City': 'New Jersey',
#        'State': 'New Jersey',
#        'Country': 'USA'
#        },
#    'Client':{
#        'Name': 'Albanese'
#        },
#    'Functions': [
#        'Residential',
#        'Commercial'
#        ],
#    'Start Date': '2018-04-21'
#    },
#'Dimensions':{
#    'Height': 120
#    }
#}
#
#
#data['Project']['Client']['Name'] = 'Test4'
#
#stream = file('Project_Info.yaml', 'w')
#yaml.safe_dump(data, stream, default_flow_style=False)
#print yaml.safe_dump(data) 
