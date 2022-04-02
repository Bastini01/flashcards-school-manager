from time import time
time1=time()
import os
import google_apps
import anki_profiles
import unused.anki_connect as anki_connect

def runNewRegistrations():

    vocabUnit=[1, 9, 2]
    startChapter=1
    state="custom1"

    studData=google_apps.getStudents()
    for i in range(len(studData)):
        if studData.loc[i, 'state']!=state:
            continue
        studActions=google_apps.getActionsTemplate()
        profileName=google_apps.getProfileName(studData, i)
        userName=studData.iloc[i, 1]
        password=userName.split("@")[0] 

        createResult=anki_profiles.createProfile(profileName)

        if createResult==False:
            print(profileName+" dup profile")
            continue
        if createResult==True:
            print(profileName+" profile created")
            conResult=anki_profiles.connectProfile(profileName, userName, password)
            if conResult==True:
                studActions=studActions.append({"studentIndex":i+2, "statusUpdate":"connected"},
                    ignore_index=True)
            else:
                studActions=studActions.append({"studentIndex":i+2, "statusUpdate":"connection failed"},
                    ignore_index=True)
            try: anki_connect.prepProfile(profileName, vocabUnit, startChapter)
            except: print("PROFILE CREATION ERROR")
            # else: 
            #     studActions=studActions.append({"studentIndex":i+2, "statusUpdate":"voc ok"},
            #           ignore_index=True)

            print("Profile created")# (",(i+1),"/",len(studData),")")
        google_apps.SendStudentActions(studActions)
    print("Profile creation finished")

runNewRegistrations()

time2=time()
print("runtime: ",int(time2-time1)," sec")
# os.system("pause")
