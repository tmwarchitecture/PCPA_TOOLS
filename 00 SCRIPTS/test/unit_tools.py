import rhinoscriptsyntax as rs

def ConvertImperialLength(numberString, ToInches = True):
    """
    ConvertLength(numberString, ToInches = True)
    -Acceptable formats:
        4.5'
        36.1"
        4'6"
    """
    if ToInches:
        footScale = 12
        inchScale = 1
    else:
        footScale = 1
        inchScale = 1/12
    if '"' in numberString and "'" in numberString:
        if numberString.find("'") < numberString.find('"'):
            try:
                values = numberString.split("'")
                feetInches = float(values[0])*footScale
                inches = float(values[-1].split('"')[0])*inchScale
                return feetInches + inches
            except:
                pass
    elif "'" in numberString:
        try:
            return float(numberString.split("'")[0])*footScale
        except:
            pass
    elif '"' in numberString:
        try:
            return float(numberString.split('"')[0])*inchScale
        except:
            pass
    return None


dim = rs.GetString("Input a dimension")
print ConvertImperialLength(dim, True)