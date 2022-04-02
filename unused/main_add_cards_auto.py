from datetime import datetime
from time import time
time1=time()
import os
import google_apps
#import anki_profiles
import anki_db
import mtc_info
import unused.anki_connect as anki_connect
#import pandas as pd
    
# print(getUnitsToAdd("00017 Ali Watak", 2)) 
   

#getUnitsToAdd("00026 Emmanuel Trenado", 1)

def runAddCards():

    vocabUnit=[6,7,1]
    startUnit=None
    studData=google_apps.getStudents()
    for i in range(len(studData)):
        if studData.loc[i, 'state']=="active":
            studActions=google_apps.getActionsTemplate()
            profileName=google_apps.getProfileName(studData, i)
            print(profileName)
            classType=studData.iloc[i, 6]
            # anki_connect.load(profileName)
            timeA=time()
            units=mtc_info.getUnitsToAdd(profileName, classType)

            if units:
                for i in units:
                    print(i)
            # anki_connect.addNotes(profileName, vocabUnit, startUnit)
            
            # studActions=studActions.append({"studentIndex":i+2, "chapterUpdate":vocabUnit},
            #       ignore_index=True)
            # print(profileName+": "+str(vocabUnit)+" added ",int(time()-timeA)," sec")
            # google_apps.SendStudentActions(studActions)
    print("Cards added")

runAddCards()
##print(google_apps.getStudents())
##anki_connect.load("2 Estiem PH")
##google_apps.SendStudentActions(google_apps.getActionsTemplate())
##print("runtime: ",int(time()-time1)," sec")
time2=time()
print("runtime: ",int(time2-time1)," sec")
#os.system("pause")
