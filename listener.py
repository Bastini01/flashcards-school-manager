# FOR TESTING PURPOSES

from datetime import datetime as dt
import time
import sys
from os.path import expanduser, join

def act(id):
    # time.sleep(10)

    original_stdout = sys.stdout
    logFilePath=join(r'C:\inetpub\wwwroot\afc\log',"test"+dt.now().strftime('%y%m%d%H%M')+".txt")


    logFile = open(join(logFilePath),'w', encoding="utf-8")
    sys.stdout = logFile
    print(str(id))
    logFile.close()
    sys.stdout = original_stdout

# act('jkl')



