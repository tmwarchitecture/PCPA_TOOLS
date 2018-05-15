import rhinoscriptsyntax as rs

def NumberToInch(numberString):
    segments = numberString.split("'")
    number = 0
    for each in segments:
        try:
            number = int(each)*12
        except:
            pass
    finalFloat = number
    return finalFloat

dim = rs.GetString("Input a dimension")
print NumberToInch(dim)