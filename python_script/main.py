from time import time

from attr import s
time1=time()
import sys
from os.path import expanduser, join
technicalFilesPath = expanduser("~")+r'\OneDrive\SRL\TechnicalFiles'

import datetime as dt
import traceback
import google_apps as g
import anki_profiles
import pandas as pd
import anki_db
import mtc_info
import class_stats, main_stats

logPath = technicalFilesPath+r'\Log'
original_stdout = sys.stdout
today=dt.datetime.now().date()
term = mtc_info.get_current_term()['term']

def main(log=True, std=True, cls=True, new=False, idFilter=None, forceConnect=False):
    if log: 
        logFilePath=join(logPath,"log"+dt.datetime.now().strftime('%y%m%d%H%M')+".txt")
        if idFilter: logFilePath = logFilePath.replace('.txt', '-'+idFilter+'.txt')
        logFile = open(join(logFilePath),'w', encoding="utf-8")
        sys.stdout = logFile
    try:
        if idFilter: forceConnect=True
        studData=g.getStudents()
        emailLog=g.getEmailLog()
        supHoursLog=g.get_sup_hours_log()
        gData=g.getData()
        gClass=gData['class']
        st_cl_te = g.st_cl_te(term, studData, gData)
        if std:
            #####ITERATE STUDENTS
            allReviews = []
            amountSynced = 0
            for i in range(len(studData)):
                profileName=studData.loc[i, 'profileName']
                studentId=studData.loc[i, 'studentId']
                email=studData.iloc[i, 1]
                oth=studData.loc[i, 'other']
                status=studData.loc[i, 'state']
                statusDate=studData.loc[i, 'statusDate']
                classType=g.class_type(profileName, st_cl_te)
                startUnit=g.start_unit(profileName, st_cl_te)
                actions=[]
                c = False
                
                ######GENERAL FILTER
                if status[0]=="t": continue
                elif new==True: 
                    if status[:3]!="new": continue
                elif idFilter:
                    if studentId!=idFilter: continue
                if i < 14: continue
                ###################
                try:
                    #########SEND REGISTRATION REMINDER
                    if status[:-1] == 'reg':
                        regResp=anki_profiles.reminder_schedule(status, statusDate, False)
                        if not regResp: continue
                        else: 
                            actions.append({"studentIndex":i+2, "emailTemplate":'regReminder',"statusUpdate":'reg'+regResp})
                            g.sendActions(actions, profileName)
                            continue
                    
                    #########ASK CLASS DATA UPDATE
                    if (status == 'active' and not classType and g.checkEmail(emailLog, studentId, 'termUpdate'+term)==False):
                            actions.append({"studentIndex":i+2, "emailTemplate": 'termUpdate'+term})
                    
                    #########CREATE PROFILE
                    if status[:3]=='new' or profileName not in anki_profiles.getProfiles():
                        created=anki_profiles.createProfile(profileName)
                    else: created=False
                            
                    #########CONNECT
                    if status[:-1]=='connection failed' or created:
                        # continue
                        c=anki_profiles.handle_connection(profileName, email, status, statusDate, oth, forceConnect)
                        if isinstance(c, str):
                            actions.append({"studentIndex":i+2,
                            "emailTemplate": 'wrongPassword', 
                            "statusUpdate":'connection failed'+c})
                        elif c is None: continue
                        elif c==True:
                            print(profileName, "new successful connection")
                            actions.append({"studentIndex":i+2,"statusUpdate":'active'})
                            try: anki_profiles.first_sync(profileName)
                            except Exception as e:
                                c = False
                                print(profileName, e)
                                naResponse = anki_profiles.handle_not_activated(status, statusDate, forceConnect)
                                if not naResponse: continue
                                else: actions=[{"studentIndex":i+2,
                                "emailTemplate": 'notActivated', 
                                "statusUpdate":'connection failed'+naResponse}]


                    #########ADD CARDS
                    if not anki_db.getLastUnit(profileName): anki_profiles.prep_profile(profileName)
                    if ((status=='active' or c==True) and classType):            
                        unitsToAdd=mtc_info.getUnitsToAdd(profileName, startUnit=startUnit, classType=classType)           
                        for u in unitsToAdd:
                            addResponse=anki_profiles.add_notes(profileName, u)
                            if addResponse==True and status=='active': 
                                actions.append({"studentIndex":i+2, "chapterUpdate":u})
                            elif addResponse==False: print(profileName, u, 'ADD NOTES PROBLEM')

                    #########SYNC    
                    if status=='active' or status[:-1]=='custom' or c==True:     
                        syncResponse = anki_profiles.sync(profileName)
                        if syncResponse == 'ok': amountSynced = amountSynced+1
                        if syncResponse=='ok' and c==True:
                            actions.append({
                            "studentIndex":i+2,
                            "emailTemplate": 'activatedMail'})
                        elif syncResponse == 'not activated': 
                            naResponse = anki_profiles.handle_not_activated(status, statusDate)
                            if not naResponse: continue
                            else: actions=[{"studentIndex":i+2,
                            "emailTemplate": 'notActivated', 
                            "statusUpdate":'connection failed'+naResponse}]
                        elif syncResponse == 'nok': 
                            actions=[{"studentIndex":i+2, "statusUpdate":'connection failed0'}]
                        elif syncResponse=="fullSync": continue
                                
                    #########NOTIFICATIONS&SUPPHOURS
                    if (status=='active' or status[:-1]=='custom') and syncResponse == 'ok':
                        rvs=anki_db.getReviews(profileName)
                        #########NO REVIEWS REMINDERS
                        if ((len(rvs)==0 or 
                            anki_db.last_review_date(rvs)+dt.timedelta(weeks=5)<today) and
                            classType):
                            #########REMINDER0
                            if (g.checkEmail(emailLog, studentId, 'reminder0')==False and
                            today >= statusDate+dt.timedelta(days=4)):
                                actions.append({"studentIndex":i+2,"emailTemplate":'reminder0'})
                            #########ACCREMINDER
                            accReport=mtc_info.acc_report(profileName, rvs, startUnit, classType)
                            if (accReport and g.checkEmail(emailLog, studentId, accReport[0])==False and
                            today >= statusDate+dt.timedelta(days=7)):
                                actions.append({"studentIndex":i+2,
                                    "emailTemplate":accReport})
                        #########REVIEW REPORTS
                        elif len(rvs)>0 and today<anki_db.last_review_date(rvs)+dt.timedelta(weeks=5): 
                            weekly=anki_db.weeklyReport(profileName, rvs)
                            daily=anki_db.dailyReport(profileName, rvs)
                            month=anki_db.month_report(profileName, rvs)
                            if daily[1]['reviews'] > 0: 
                                print(profileName, str(daily[1]['reviews'])+' revs')
                            ########WEEKLY REPORT
                            if (g.checkEmail(emailLog, studentId, weekly[0])==False and
                                    anki_db.weekly_send_conditions(rvs, weekly)):                    
                                    actions.append({"studentIndex":i+2,"emailTemplate":weekly})
                            ########DAILY REPORT
                            elif (g.checkEmail(emailLog, studentId, daily[0])==False and
                                daily[1]['reviews'] > 1 and
                                len(daily[1]['completion'][1]) > 0 and
                                len(rvs)<500):
                                    actions.append({"studentIndex":i+2,"emailTemplate":daily}) 
                            ########SUPPLEMENTARY HOURS
                            sh=g.get_student_sup_hours(supHoursLog, studentId)
                            h = month[1]['hours']-sh if sh+month[1]['hours']<=8 else 8-sh
                            if h>0: actions.append({"studentIndex":i+2, 
                                "emailTemplate":'suppHours'+str(h)+str(sh)})   
                    #########SEND TO GAPPS
                    if len(actions)>0: g.sendActions(actions, profileName)
                    # if len(actions)>0: print(actions)
                    #########APPEND REVIEWS
                    allReviews = allReviews+anki_db.getReviews(profileName)
                except Exception as e: 
                    tb = traceback.format_exc()
                    print(profileName, tb, e)

            allReviewsDf=anki_db.rev_to_df(allReviews)
            # df.to_csv("allReviews.txt")

            print("STUDENTS DONE; "+str(amountSynced)+" synced")
        if cls and not new and not idFilter:
        #####ITERATE CLASSES
            def class_actions(classId, teacherId):
                try:
                    wc=class_stats.class_report(classId, True, st_cl_te)
                    del wc[1]['styler']
                    if (not wc[1]['empty'] and wc[1]['teacherEmail'] != "-" and
                    g.checkEmail(emailLog, teacherId, "cw"+wc[1]['class']+wc[1]['timeFrame'])==False):
                        g.sendActions([{"emailTemplate":wc}])
                except Exception as e: 
                    tb = traceback.format_exc(limit=50)
                    print(classId, teacherId, tb, e)

            c=gClass
            df=c[c['term']==mtc_info.get_current_term()['term']]
            df.apply(lambda x: class_actions(x['class_id'], x['teacher_id']), axis=1)
            
            print("CLASSES DONE")

            if today.isoweekday() == 1:
                main_stats.trendWeekly(allReviewsDf)

        time2=time()
        print("runtime: ",int(int(time2-time1)/60)," min")
    except Exception as e: 
        tb = traceback.format_exc()
        print(tb, e)
    if log:
        logFile.close()
        sys.stdout = original_stdout
        # SEND LOG
        with open(logFilePath, 'r', encoding="utf-8") as file:
            logdata = file.read()
        g.sendActions([{"emailTemplate":('log', logdata)}])
        htmllogdata = "<p>" + logdata.replace("\n", "<br>") + "</p>"
        return htmllogdata
    
def add_book(sId, book):

    logFilePath=join(logPath,"log_add_book"+dt.datetime.now().strftime('%y%m%d%H%M')+".txt")
    logFile = open(join(logFilePath),'w', encoding="utf-8")
    sys.stdout = logFile
    try:
        studData=g.getStudents()
        studentIndex = studData.loc[studData['studentId'] == sId].index.values[0]
        # profileName = studData.loc[studData['studentId'] == sId, 'profileName'].values[0]
        profileName=studData.loc[studentIndex, 'profileName']
        unitsToAdd=mtc_info.getUnitsToAdd(profileName, book = book)
        for u in unitsToAdd:
            addResponse=anki_profiles.add_notes(profileName, u)
            if addResponse==False: raise Exception(profileName, u, 'ADD NOTES PROBLEM')
        syncResponse = anki_profiles.sync(profileName)
        if syncResponse != 'ok': raise Exception(profileName, 'SYNC ISSUE')
        print(profileName+' book '+book+' added and synchronized')
        g.sendActions([{"studentIndex":studentIndex+2, "emailTemplate":'bookAdded'+book}])

    except Exception as e: tb = traceback.format_exc(); print(e, tb) 
    logFile.close()
    sys.stdout = original_stdout
    with open(logFilePath, 'r', encoding="utf-8") as file:
        logdata = file.read()

    g.sendActions([{"emailTemplate":('log', logdata)}])
    return
    



