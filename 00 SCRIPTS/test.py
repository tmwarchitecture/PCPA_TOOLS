import os
import hashlib
import rhinoscriptsyntax as rs

def Authorize():
    root = os.path.join(os.environ['appdata'], "PCPA")
    if not os.path.isdir(root):
        os.makedirs(root)
    while True:
        password = rs.GetString("Enter PCPA Rhino Toolbar license key")
        if password is None: return False
        hash = hashlib.sha224(password).hexdigest()
        key = '7bce017b9e1c5f1a3a73d8edfb7e47505a39375cb0f83e89c48f9c55'
        
        if hash == key:
            print "Computer Authorized"
            authFile = os.path.join(root, 'authorize.pcpa')
            file = open(authFile,'w')
            file.write("True")
            file.close()
            return True
        else:
            print "Incorrect password"

def IsAuthorized():
    authFile = os.path.join(os.environ['appdata'], "PCPA", 'authorize.pcpa')
    if os.path.isfile(authFile):
        file = open(authFile,'rb')
        if file.readline() == "True":
            file.close()
            return True
        file.close()
        return False
    elif os.path.isdir():
        utils.GetNetworkLocation()
    else:
        return Authorize()

def CheckAuth():
    

IsAuthorized()

print IsAuthorized()