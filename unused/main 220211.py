from time import time
import datetime as dt
time1=time()
import os
import traceback
import google_apps as g
import anki_profiles
import pandas as pd
import anki_db
import mtc_info
import class_stats

today=dt.datetime.now().date()

def main():
    studData=g.getStudents()
    emailLog=g.getEmailLog()
    allReviews = []
    ######ITERATE STUDENTS
    for i in range(len(studData)):
        profileName=studData.loc[i, 'profileName']
        studentId=studData.loc[i, 'studentId']
        email=studData.iloc[i, 1]
        status=studData.loc[i, 'state']
        statusDate=studData.loc[i, 'statusDate']
        classType=studData.loc[i, 'classType']
        startUnit=studData.loc[i, 'startUnit']
        startDate=studData.loc[i, 'startDate']
        studActions=g.getActionsTemplate()
        
        ######GENERAL FILTER
        if status[0]=="t": continue
        # if i+1!=53: continue
        # if i+1 not in [65, 69, 89]: continue
        # if i < 10: continue
        # if status!="active": continue
        ###################
        try:
            #########CREATE PROFILE
            if status=='new':
                created=anki_profiles.createProfile(profileName)
                anki_profiles.add_notes(profileName, startUnit, 1)
            
            #########ADD CARDS
            if status=='active' or status[:-1]=='connection failed' or status=='new':            
                unitsToAdd=mtc_info.getUnitsToAdd(profileName, startUnit, startDate, classType)           
                for u in unitsToAdd:
                    addResponse=anki_profiles.add_notes(profileName, u)
                    if addResponse==True and status=='active': 
                        studActions=studActions.append({"studentIndex":i+2, "chapterUpdate":u}, ignore_index=True)
                        print(profileName, u, 'cards added')
                    elif addResponse==False: print(profileName, u, 'ADD NOTES PROBLEM')

            #########CONNECT
            if status[:-1]=='connection failed' or status=='new':
                # continue
                c=anki_profiles.handle_connection(profileName, email, status, statusDate)
                if isinstance(c, str):
                    studActions= studActions.append({
                    "studentIndex":i+2,
                    "emailTemplate": 'wrongPassword', 
                    "statusUpdate":'connection failed'+c}, 
                    ignore_index=True)
                elif c is None: continue
                elif c==True:
                    print(profileName, "new successful connection")
                    studActions= studActions.append({
                    "studentIndex":i+2,
                    "statusUpdate":'active'}, 
                    ignore_index=True)

            #########SYNC    
            if status=='active' or status[:-1]=='custom' or (status=='new' and c==True):     
                syncResponse = anki_profiles.sync(profileName, status)
                if syncResponse and status=='new':
                    studActions= studActions.append({
                    "studentIndex":i+2,
                    "emailTemplate": 'activatedMail', 
                    "statusUpdate":'active'}, 
                    ignore_index=True)
                elif not syncResponse: 
                    studActions.drop(studActions.index, inplace=True)
                    studActions= studActions.append({
                        "studentIndex":i+2, 
                        "statusUpdate":'connection failed0'}, 
                        ignore_index=True)

            #########NOTIFICATIONS
            if status=='active' or status[:-1]=='custom':
                rvs=anki_db.getReviews(profileName)
                #########REMINDER0
                if len(rvs)==0:
                    if (g.checkEmail(emailLog, studentId, 'reminder0')==False and
                    today >= statusDate+dt.timedelta(days=7)):
                        studActions= studActions.append({
                            "studentIndex":i+2, 
                            "emailTemplate":'reminder0'}, 
                            ignore_index=True)
                #########WEEKLY REPORT
                else: 
                    weekly=anki_db.weeklyReport(rvs)
                    if (g.checkEmail(emailLog, studentId, weekly[0])==False and
                    weekly[1]['reviews'] > 1):
                        studActions= studActions.append({
                            "studentIndex":i+2, 
                            "emailTemplate":weekly}, 
                            ignore_index=True)
            
            #########SEND TO GAPPS
            if not studActions.empty: g.SendStudentActions(studActions)
            # print(studActions)
            #########APPEND REVIEWS
            allReviews = allReviews+anki_db.getReviews(profileName)
        except Exception as e: 
            tb = traceback.format_exc(limit=1)
            print(profileName, tb)

    df=anki_db.rev_to_df(allReviews)
    df.to_csv("allReviews.txt")

    print("STUDENTS DONE")

    ######ITERATE CLASSES
    class_stats.gClass['class_id'].apply(
    lambda x:
    class_stats.class_report(x, 'week')
    )




main()

time2=time()
print("runtime: ",int(int(time2-time1)/60)," min")
#os.system("pause")
