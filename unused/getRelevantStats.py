import json
import urllib.request
import pandas as pd
#import time
from datetime import date

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def extractStats():
    today = date.today()
    yymmddDate = today.strftime("%y%m%d")
    ProfileList=invoke('getProfiles')
    d=[]
    for profileName in ProfileList:
    #profileName="PH Main user"
        invoke('loadProfile', name=profileName)
        dueCards=invoke('findCards',query='is:due')
        dueCardsAmnt=len(dueCards)
        matureCards=invoke('findCards',query='prop:ivl>=21')
        matureCardsAmnt=len(matureCards)
        suspendedCards=invoke('findCards',query='is:suspended')
        suspendedCardsAmtn=len(suspendedCards)
        allCards=invoke('findCards',query='')
        totalCards=len(allCards)
        otherCardsAmnt=len(allCards)-suspendedCardsAmtn-matureCardsAmnt
    #    print (dueCardsAmnt,matureCardsAmnt,suspendedCardsAmtn,otherCardsAmnt)
        d.append(
            {
                'Student': profileName,
                'Cards due': dueCardsAmnt,
                'Cards mature': matureCardsAmnt,
                'Cards suspended': suspendedCardsAmtn,
                'Cards other': otherCardsAmnt,
                'Cards total': totalCards
            }
        )

    df=pd.DataFrame(d)
    xlsxName="teacher_stats_"+yymmddDate+".xlsx"
    df.to_excel(xlsxName)
#print('got list of decks: {}'.format(result))
    print("end")
