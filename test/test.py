import sys
import os
import rhinoscriptsyntax as rs
print sys.version
print sys.version_info
print sys.platform

programs = os.listdir(r'C:\Program Files (x86)')
for program in programs:
    if program[:5] == "IronP":
        print program
print "Build date:" + str(rs.BuildDate())
print "SDK Version:"+ str( rs.SdkVersion())
print "Executable Version:", rs.ExeVersion()
print "Executable Service Release:", rs.ExeServiceRelease()


rs.EnableRedraw(False)
#print "New layer:", rs.AddLayer("MyLayer3")
print "New layer:", rs.AddLayer("MyLayer3::MyLayer4")
rs.EnableRedraw(True)