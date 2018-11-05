import rhinoscriptsyntax as rs
import pprint

def DesignHistoryToList(history):
    return history.split("<--")

history = r'181105_OPTION_01<--181105_OPTION_02<--181105_OPTION_03<--181105_OPTION_04<--181105_OPTION_05'    
iterations = DesignHistoryToList(history)
print iterations
DesignHistory = {}
DesignHistory[iterations[0]] = {}
DesignHistory[iterations[0]][iterations[1]] = {}
DesignHistory[iterations[0]][iterations[1]][iterations[2]] = {}

print DesignHistory
if '181105_OPTION_03' in DesignHistory:
    print "YEP"