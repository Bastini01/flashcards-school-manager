# from __future__ import print_function
from time import sleep
from datetime import datetime as dt, date as da
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import errors
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
import pandas as pd
import anki_db as db

today=dt.now().date()

Script_ID ='1YTY8-oBmV3a9SChEDsYIPbmkINxQNitY8U5nAmAukBFXyu1nb0xjN6lE' ##script id

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/script.scriptapp',
          'https://www.googleapis.com/auth/spreadsheets.currentonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://mail.google.com/',
          'https://www.googleapis.com/auth/gmail.addons.current.action.compose',
          'https://www.googleapis.com/auth/script.external_request',
          'https://www.googleapis.com/auth/forms',
          'https://www.googleapis.com/auth/script.deployments']
# Set up the Apps Script API
store = oauth_file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)

def getProfileName(data, i):
    profileName = str(i+1).zfill(5)+" "+data.iloc[i, 2]+" "+data.iloc[i, 3].rstrip()
    chars= "\/?"
    mytable = profileName.maketrans(chars, "   ")
    profileName = profileName.translate(mytable)
    # profileName=profileName.replace("/","")
    return profileName

def str_2_d(x):
    return dt(int(x.split('/')[2][:4]), int(x.split('/')[0]), int(x.split('/')[1])).date()

def status_date(data, i):
    d0=data.loc[i, 'Last update date']
    if not d0: return None
    d1=str_2_d(d0)
    return d1

def unit_date(data, i):
    d=data.iloc[i, 9].split('-')[1]
    startUnit=[int(data.iloc[i, 7]), int(data.iloc[i, 9].split('-')[0]), 1]
    startDate=dt(int('20'+d[:2]), int(d[2:4]), int(d[4:])).date()
    return {'unit':startUnit, 'date':startDate}

def get_gsheet(sheetName, 
    spreadSheet = '1zM1uvzFo4dEQ4qVSp2SRE6RC8Ll2Dw-a5GftXw2Iy18'):
    SAMPLE_SPREADSHEET_ID = spreadSheet
    SAMPLE_RANGE_NAME = sheetName
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    with open(db.technicalFilesPath+'gapps_backup_'+sheetName+'.pkl','wb') as fp:
        pickle.dump(result, fp)
    return result.get('values', [])

def getStudents():

    data = pd.DataFrame(get_gsheet("'Form Responses 1'"))
    data.columns = data.iloc[0]
    data.columns.name=None
    data.drop(index=0, inplace=True)
    data.reset_index(drop=True, inplace=True)
    for i in range(len(data)):
        data.loc[i,'profileName'] = getProfileName(data, i)
        data.loc[i,'statusDate'] = status_date(data, i)
    c=[data.columns[i] for i in [2,3,5,6,7,8,10,11,16,17]]
    c.append('Last update date')
    data.drop(columns=c, inplace=True)
    data.rename(columns={
        data.columns[2]: "studentId", 
        data.columns[3]: "os"}, 
        inplace=True)
    return(data)
getStudents().to_csv(db.technicalFilesPath+'studentsDF.csv')

def test_api():
    df = getStudents()
    df['studentId'].apply(lambda x: print(x))

def getEmailLog():
    data = get_gsheet("'Email log'")
    columnNames = data.pop(0)
    mailLog = pd.DataFrame(data, columns=columnNames)
    for i in range(len(mailLog)):
        mailLog.loc[i,'date'] = dt.strptime(mailLog.iloc[i, 0],'%m/%d/%Y').date()
    mailLog.drop(columns=['Timestamp'], inplace=True)
    return mailLog
# print(getEmailLog().columns)

def checkEmail(emailLog, recipientId, emailTemplate, startDate=None):
    df=emailLog
    startDate= da(2021,11,1) if startDate==None else startDate
    if (
        (df['recipientId'] == recipientId) & 
        (df['emailTemplate'] == emailTemplate) &
        (df['date'] >= startDate)
        ).any():
        return True
    else: return False

def getData():
        t = get_gsheet("'teacher'")
        c = get_gsheet("'class'")
        s_c = get_gsheet("'student_class'")
        l=[t ,c , s_c]
        for i in range(len(l)):
            columnNames = l[i].pop(0)
            l[i] = pd.DataFrame(l[i], columns=columnNames)
        # return i
        result= {'teacher': l[0], 'class': l[1], 'student_class': l[2]}
        return result

def st_cl_te(term = None, studData = None, gData = None):
    s = studData if studData is not None else getStudents()
    d= gData if gData is not None else getData()
    df=s.merge(d['student_class'], how='left', on='studentId')
    df=df.merge(d['class'], how='left', on='class_id')
    df1=df.merge(d['teacher'], how='left', on='teacher_id')
    if term is not None: df1=df1[df1['term']==term]
    return df1

def start_unit(profileName, st_cl_te):
    df=st_cl_te[st_cl_te['profileName']==profileName]
    if len(df) == 0: return None
    else:
        su=df.iloc[0].at['startUnit']
        startUnit=[int(su.split(",")[0]), int(su.split(",")[1]), 1] if su else None 
        return startUnit

def class_type(profileName, st_cl_te):
    df=st_cl_te[st_cl_te['profileName']==profileName]
    if len(df) == 0: return None
    classType = df.iloc[0].at['type']
    if not classType: return None
    else: return int(classType)

def get_sup_hours_log():
    data = get_gsheet("'sup_hours_log'", '1GZGz8N4a-r125qxtlcRUvlNn29OxS_0VJGvV9d8I0SE')
    columnNames = data.pop(0)
    df = pd.DataFrame(data, columns=columnNames)
    return df

def get_line_log():
    data = get_gsheet("'LINE'")
    columnNames = data.pop(0)
    df = pd.DataFrame(data, columns=columnNames)
    return df

def get_student_sup_hours(supHoursLog, studentId):
    df=supHoursLog
    df=df[df['Timestamp'].apply(lambda x: dt.strptime(x, '%m/%d/%Y %H:%M:%S').year)==da.today().year]
    df=df[df['Timestamp'].apply(lambda x: dt.strptime(x, '%m/%d/%Y %H:%M:%S').month)==da.today().month]
    df=df[df['Student number']==studentId]
    s = df['hours'].apply(lambda x: int(x)).sum()
    return s if s else 0
# (get_student_sup_hours(get_sup_hours_log(), '220312055'))

def getActionsTemplate(): #not used, documentation only
    columns={"studentIndex":[], "statusUpdate":[], "chapterUpdate":[],"emailTemplate":[]}
    return columns

def sendActions(actions, retry=True):

    service = build('script', 'v1', credentials=creds)

    ######### Create an execution request object.
    actionsJSON=pd.DataFrame(actions).to_json(orient="index")
    request = {"function": "handleDesktopRequest", "parameters": actionsJSON, "devMode": True}

    try:
        ########### Make the API request.
        response = service.scripts().run(body=request,
                scriptId=Script_ID).execute()

        ######## Attempt at automatically getting latest deployment
        # response = service.projects().deployments().list(scriptId='1YTY8-oBmV3a9SChEDsYIPbmkINxQNitY8U5nAmAukBFXyu1nb0xjN6lE').execute()
        # depId = response['deployments'][len(response['deployments'])-1]['deploymentId']
        # print(depId)

        if 'error' in response:
            # The API executed, but the script returned an error.

            # Extract the first (and only) set of error details. The values of
            # this object are the script's 'errorMessage' and 'errorType', and
            # an list of stack trace elements.
            error = response['error']['details'][0]
            print("Script error message: {0}".format(error['errorMessage']))

            if 'scriptStackTraceElements' in error:
                # There may not be a stacktrace if the script didn't start
                # executing.
                print("Script error stacktrace:")
                for trace in error['scriptStackTraceElements']:
                    print("\t{0}: {1}".format(trace['function'],
                        trace['lineNumber']))
        else:
            try:
                if response['done']==True: 
                    r="gAction done "
                    rs=str(response['response']['result'])[:200]
                else: print("gAction FAILED")    
            except: print(actions, response)

    except errors.HttpError as e:
        # The API encountered a problem before the script started executing.
        if retry: 
            sleep(10)
            sendActions(actions, False)
        else: print('http error', actions, e.content)


def send_test_action():
    action = [
        {"studentIndex":2,
        "emailTemplate":('weekly220328', 
            {
                'reviews': 0, 
                'time': '1 minute', 
                'hours': 0, 
                'tbWords': 0, 
                'chaps': 0, 
                'otbWords': 0, 'top': [], 
                'lastRev': da(2022, 3, 21), 
                'chaps-words': [], 
                'completion': (None, None), 
                'pendingLearning': [[[1, 6], 57, 0, '25 minutes'], [[1, 8], 19, 0, '8 minutes'], [[1, 9], 23, 0, '10 minutes'], [[1, 10], 20, 0, '9 minutes'], [[1, 11], 40, 0, '17 minutes']], 
                'pending': 159, 
                'learning': 0})
        }
    ]