import rhinoscriptsyntax as rs
import sys
sys.path.append(r'X:\05_RHINO STANDARDS\05 SCRIPTS\PYTHON\PCPA\PCPA\libs')
from geopy.geocoders import Nominatim

geolocator = Nominatim()

address = rs.StringBox("Enter Address")
#address = r'310 12th st, ny'

location = geolocator.geocode(address)
print(location.address)

print((location.latitude, location.longitude))
#print location.address['city']
#print(location.raw)
