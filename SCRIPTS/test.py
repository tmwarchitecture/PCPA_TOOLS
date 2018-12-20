import os
import config


fileLocations = config.GetDict()
csvPath = fileLocations['licenses']

print os.environ['COMPUTERNAME']