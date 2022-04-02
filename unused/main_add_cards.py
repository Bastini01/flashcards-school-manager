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

def getUnitsToAdd(profileName, classType):
    today=datetime.now().date()
    # print(anki_db.getLastUnit(profileName))
    lastUnitDate= anki_db.getLastUnit(profileName)[0]
    lastUnit= anki_db.getLastUnit(profileName)[1]
    n=len([i for i in mtc_info.addDates(classType) if i<=today and i>lastUnitDate])
    # print(n)
    unitsToAdd=mtc_info.UnitsAhead(lastUnit, n)
    return unitsToAdd
    
# print(getUnitsToAdd("00017 Ali Watak", 2)) 

def runAddCards():

    vocabUnit=[1,10,2]
    startUnit=10
    studData=google_apps.getStudents()
    for i in range(len(studData)):
        profileName=google_apps.getProfileName(studData, i)
        # unitCheck = mtc_info.getUnitsToAdd(profileName, studData.iloc[i, 6])
        if studData.loc[i, 'state']=="active": # and studData.iloc[i, 9]=="8p2":
        # if unitCheck[len(unitCheck)-1]==[1,10,2]:
            studActions=google_apps.getActionsTemplate()
            # print(profileName)
            # classType=studData.iloc[i, 6]
            anki_connect.load(profileName)
            timeA=time()
            # units=getUnitsToAdd(profileName, classType)

            # if units:
            #     for i in units:
            #         print(i)
            anki_connect.addNotes(profileName, vocabUnit, startUnit)
            
            studActions=studActions.append({"studentIndex":i+2, "chapterUpdate":vocabUnit},
                  ignore_index=True)
            print(profileName+": "+str(vocabUnit)+" added ",int(time()-timeA)," sec")
            try: google_apps.SendStudentActions(studActions)
            except: print("Gapps action failed")
    print("Cards added")

runAddCards()
##print(google_apps.getStudents())
##anki_connect.load("2 Estiem PH")
##google_apps.SendStudentActions(google_apps.getActionsTemplate())
##print("runtime: ",int(time()-time1)," sec")
time2=time()
print("runtime: ",int(time2-time1)," sec")
#os.system("pause")
