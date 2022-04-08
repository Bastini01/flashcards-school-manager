import time
time1=time.time()
import pandas as pd
import anki_db, anki_profiles
import google_apps

def getReviewDataAll():
    # studData=google_apps.getStudents()
    profiles = anki_profiles.getProfiles()
    allReviews = []
    # for i in range(len(studData)):
    for i in profiles:
        profNum=int(i[2:5])
        # state=studData.loc[i, 'state']
        # if state=="active": #or state[:-1]=="custom":
        # if state[0] != 't':
        if profNum > 3 and profNum not in [13, 14, 15, 18]:
            # profileName=studData.loc[i, 'profileName']
            profileName = i
            try:allReviews = allReviews+anki_db.getReviews(profileName)
            except Exception as e:
                if "no such table: revlo" in str(e): continue
                print(profileName+" EXCEPTION: extraction issue!", e)
                continue

    df= anki_db.rev_to_df(allReviews)   
    # df = df[df.student != '']
    return df

# rev=getReviewDataAll()
# rev.to_csv("allReviews.txt")
# rev.to_pickle("allReviews.pkl")
# time2=time.time()
# print("runtime: ",int(time2-time1)," sec")
# print("end")
