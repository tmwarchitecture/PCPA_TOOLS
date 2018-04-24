import sys
import os
print sys.version
print sys.version_info
print sys.platform

programs = os.listdir(r'C:\Program Files (x86)')
for program in programs:
    if program[:5] == "IronP":
        print program