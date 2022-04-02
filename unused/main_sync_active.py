from time import time
time1=time()
import os
import google_apps
import anki_profiles
import unused.anki_connect as anki_connect
import pandas as pd

def runSyncActive():
###################
    state='active'
    allowFullUpload=False  ####CAREFUL WITH THAT, CAN POTENTIALLY OVERWRITE STUDENT'S EXISTING DATA!!
##################""

    studData=google_apps.getStudents()
    studActions=google_apps.getActionsTemplate()
    for i in range(len(studData)):
        if studData.loc[i, 'state']==state:
            profileName=google_apps.getProfileName(studData, i)
            c=anki_profiles.sync(profileName, allowFullUpload)
            # anki_connect.load(profileName)
            # anki_connect.sync()
            if c==True:
                studActions=studActions.append({"studentIndex":i+2, "statusUpdate":"active"},
                    ignore_index=True)
            else:
                studActions=studActions.append({"studentIndex":i+2, "statusUpdate":"connection failed"},
                    ignore_index=True)
            try: google_apps.SendStudentActions(studActions)
            except: print('gAction failed')
            studActions = studActions.drop([0])
    print("Sync finished")
    return studActions


runSyncActive()

time2=time()
print("runtime: ",int(time2-time1)," sec")
# os.system("pause")
