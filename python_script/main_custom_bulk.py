from time import time
import datetime as dt
time1=time()
import os
import google_apps as g
import anki_profiles, config_deck
import unused.anki_connect as anki_connect
import pandas as pd
import anki_db
import mtc_info

def runCustomBulk():
    studData=g.getStudents()
    count=0
    OnePlusReviews=0
    lst=[]

    for i in range(len(studData)):
        timeA=time()
        profileName=studData.loc[i, 'profileName']
        email=studData.iloc[i, 1]
        status=studData.loc[i, 'state']
        statusDate=studData.loc[i, 'statusDate']
        # classType=studData.loc[i, 'classType']
        # startUnit=studData.loc[i, 'startUnit']
        # startDate=studData.loc[i, 'startDate']

        
        
        # if studData.loc[i, 'state']=="active":
        # if status[0]!="t":
        # if profileName == "00043 Youko Martinez":
        if profileName == "":
        # if studData.loc[i, 'class']=="907":
        # if profileName[:5] == "00100":
        # if studData.loc[i, 'state']=="active" and unitsToAdd !=[[4, 1, 1], [4, 1, 2], [4, 2, 1]]:
            # print(profileName)
            # anki_profiles.createModel(profileName, "dict")
            # anki_profiles.createModel(profileName, "recall")
            # anki_profiles.saveDeckConfig(profileName, config_deck.getConfig('Default', 1))

            # userName=studData.iloc[i, 1]           
            # password=userName.split("@")[0]
            # anki_profiles.connectProfile(profileName, userName, password)

            # print(anki_db.getLastUnit(profileName))

            # print(profileName, [i[1] for i in anki_db.getUnits(profileName)])
            # try:
            #     unitsToAdd=mtc_info.getUnitsToAdd(profileName, startUnit, startDate, classType)
            #     if unitsToAdd!=[]: print(profileName, unitsToAdd)
            # except: print('error')

            # unitsToAdd=[[1,4,2]]
            
            # for u in unitsToAdd:
            #     addResponse=anki_profiles.add_notes(profileName, u)
            #     if addResponse==True: 
            #         studActions=studActions.append({"studentIndex":i+2, "chapterUpdate":u}, ignore_index=True)
            # syncResponse = anki_profiles.sync(profileName)
            # if syncResponse == True: google_apps.SendStudentActions(studActions)

            anki_profiles.add_notes(profileName, [1,5,2], 1)
            # try: anki_profiles.sync(profileName)
            # except: print('sync error')
            # anki_profiles.deleteDeck(profileName, [1,9])
            #google_apps.SendStudentActions(studActions)
            #print(profileName+": DONE ",int(time()-timeA)," sec")

            # print(profileName, len(anki_db.getReviews(profileName)))
            # if len(anki_db.getReviews(profileName))>200:
            #     lst.append(i)
            #     print(anki_db.mean_time_first_review(profileName))
            #     means.append(anki_db.mean_time_first_review(profileName))
                # anki_db.first_review_completion_report(profileName)

            # count=count+1

            # reviews= anki_db.getReviews(profileName)
            # if len(reviews)>0: OnePlusReviews=OnePlusReviews+1
    # lst=[x+2 for x in lst]
    # print(lst)            
    # print(sum(means)/len(means))
    # print('active:', count, 'OnePlusReviews:', OnePlusReviews)
    
    print("Bulk actions done")

runCustomBulk()

time2=time()
print("runtime: ",int(time2-time1)," sec")
#os.system("pause")
