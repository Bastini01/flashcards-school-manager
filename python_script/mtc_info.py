import numpy as np
import datetime as dt
import math
import anki_db
import os
import config_notes

termStartUnits=[[1,1,1],[1,6,1],[2,1,1],[2,6,1],[2,11,1],[3,9,1],[4,1,1]]

def dateList(sdate, edate):
    return [sdate+dt.timedelta(days=x) for x in range((edate-sdate).days+1)]

now=dt.datetime.now()
today=now.date()

businessDaysPerTerm=45 #actually 57, tweaked to match the actual speed of progress

 ####x days sooner to accomodate early registrations
fallDate=[9, 2]
winterDate=[12, 1]
springDate=[3, 7]
summerDate=[6, 3]
########
bdc=np.busdaycalendar(holidays = [
    *[dt.date( today.year, 1, 1 ), dt.date( today.year, 1, 2 )], #'nyJan': 
    *dateList(dt.date( today.year, 1, 20 ), dt.date( today.year, 1, 28)), #'cny': 
    *dateList(dt.date( today.year, 4, 1 ), dt.date( today.year, 4, 5)), #'springBreak': 
    *dateList(dt.date( today.year, 6, 22 ), dt.date( today.year, 6, 25)), #dragon boat holiday
    *dateList(dt.date( today.year, 8, 24), dt.date( today.year, 8, 31)), #'summerHoliday' : 
    dt.date( today.year, 9, 9 ), #'midAtumn' : 
    dt.date( today.year, 10, 10 ), #'doubleTen' : 
    *dateList(dt.date(today.year, 11, 24), dt.date(today.year, 11, 30)), #'fallBreak' : 
    dt.date( today.year, 12, 31 ) #'nyDec' : 
    ])

def month_end():
   monthLastDay = dt.date(today.year, today.month+1 if today.month != 12 else 1, 1)
   dateLast = np.busday_offset(monthLastDay, -2, roll='backward', busdaycal=bdc).astype(dt.date) #last day for getting supplementary hours+1 day
   x = np.busday_offset(monthLastDay, -3, roll='backward', busdaycal=bdc)
   datePrint = x.astype(dt.datetime).strftime('%a %d-%b')
   dateReminder = np.busday_offset(monthLastDay, -6, roll='backward', busdaycal=bdc).astype(dt.date)
   return {'lastDay':dateLast, 'reminderDate':dateReminder, 'printDate':datePrint}

def get_term(d):
    if d.month==12:
        termStart= dt.date( d.year, winterDate[0], winterDate[1])
        termEnd= dt.date( d.year+1, springDate[0], springDate[1])
        term=str(termStart.year)[2:]+"winter"
    elif d.month < 3 or d.month==3 and d.day< springDate[1]:
        termStart= dt.date( d.year-1, winterDate[0], winterDate[1])
        termEnd= dt.date( d.year, springDate[0], springDate[1])
        term=str(termStart.year)[2:]+"winter"
    elif d < dt.date( d.year, summerDate[0],summerDate[1]):
        termStart= dt.date( d.year, springDate[0], springDate[1])
        termEnd= dt.date( d.year, summerDate[0],summerDate[1])
        term=str(termStart.year)[2:]+"spring"
    elif d < dt.date( d.year, fallDate[0],fallDate[1]):
        termStart= dt.date( d.year, summerDate[0], summerDate[1])
        termEnd= dt.date( d.year, fallDate[0],fallDate[1])
        term=str(termStart.year)[2:]+"summer"
    else: 
        termStart= dt.date( d.year, fallDate[0], fallDate[1])
        termEnd= dt.date( d.year, winterDate[0], winterDate[1])
        term=str(termStart.year)[2:]+"fall"
    return {'term': term, 'termStart': termStart, 'termEnd': termEnd}

termStart = get_term(today)['termStart']

def get_term_dates(term):
    year = int("20"+term[:2])
    season = term[2:]
    if season == "winter": d1 = winterDate ; d2 = springDate
    elif season == "spring": d1 = springDate ; d2 = summerDate
    elif season == "summer": d1 = summerDate ; d2 = fallDate
    else: d1 = fallDate; d2 = winterDate
    result = {'termStart': dt.date(year, d1[0], d1[1]), 
              'termEnd': dt.date(year, d2[0], d2[1])}
    if season == "winter": result['termEnd'] = dt.date(year+1, d2[0], d2[1])
    return result

def unit_to_zh(vocabUnit):
    txt="當代"+str(vocabUnit[0])
    if len(vocabUnit)>1: txt=txt+"-"+str(vocabUnit[1])
    if len(vocabUnit)==3: txt=txt+"-第"+str(vocabUnit[2])+"部分"
    return txt

def last_unit_of_book(vocabUnit):
    if vocabUnit[0]==1 or vocabUnit[0]==2: return [vocabUnit[0],15,2]
    elif vocabUnit[0]==3 or vocabUnit[0]==4: return [vocabUnit[0],12,2]
    elif vocabUnit[0]==5: return [5,10,2]

def nextUnit(vocabUnit):
    vu=vocabUnit
    if vu==[5,10,2]:
        return vu
        
    if vu[2]==1: 
        vu[2]=2
        return vu
    else: vu[2]=1

    if (((vu[0]==1 or vu[0]==2) and vu[1]==15) or
        ((vu[0]==3 or vu[0]==4) and vu[1]==12)):
        vu[0]=vu[0]+1
        vu[1]=1
        return vu

    else: vu[1]=vu[1]+1
    return vu

def unitAhead(vocabUnit, numberOfUnits=None):
    vu=vocabUnit
    if not numberOfUnits: return nextUnit(vu)

    for i in range(numberOfUnits):
        vu=nextUnit(vu)
    return vu

def listUnits(vocabUnit, numberOfUnits): #list of units ahead
    vu=vocabUnit
    l=[list(vocabUnit)]
    for i in range(numberOfUnits+1):
        if i==0: continue
        l.append(list(nextUnit(vu)))
    return l

def vocabUnit(unitNr):
    return listUnits([1,1,1], 127)[unitNr]

def unitNr(vocabUnit):
    return listUnits([1,1,1], 127).index(vocabUnit)

def countAllUnits():
    unit=[1,1,1]
    x=0
    for i in range(1000):
        if unit==[5,10,2]:
            return x
        x=x+1
        unit=unitAhead(unit)

def termStartUnit(vocabUnit): #doesn't work
    unit=[1,1,1]
    tsu=[1,1,1]
    for i in range(127):
        if (unit in termStartUnits):
            tsu=unit
            # print(tsu)
        if unit==vocabUnit:
            break  
        unit=unitAhead(unit)

def addDays(startUnit, classType=2): # list [of int]
    bd = businessDaysPerTerm
    days=[[0, list(startUnit)]]
    unitList = listUnits(startUnit, 29)
    d=0
    for u in unitList[1:]:
        # print(bd)
        if u[0]==1 or u[0]==2: incr=bd/30    
        elif u[0]==3 or u[0]==4: incr=bd/24
        else: incr=bd/24
        if classType==2: incr=incr*(3/2)
        d=d+incr
        if d>=bd: break
        days.append([math.floor(d), u])
    return days 

def addDates(startUnit, startDate, classType):
    dl=dateList(startDate, startDate+dt.timedelta(days=100))
    bdl=[dl[i] for i in range(len(dl)) if np.is_busday(dl[i], busdaycal=bdc)]
    units = addDays(startUnit, classType)
    return [[bdl[u[0]], u[1]] for u in units] 
# print(addDates([2,11,1], termStart,2))

def currentUnit(date, startUnit, startDate, classType):
    du=addDates(startUnit, startDate, classType)
    for i in du:
        if i[0]<=date:
            u=i[1]
    return u
# print(currentUnit(today, [2,11,1], termStart, 2))

def getUnitsToAdd(profileName, startUnit=None, classType=None, book=None): 
    date=today
    startDate = termStart
    presentUnits = [x[1] for x in anki_db.getUnits(profileName)]
    if not book:
        unitsToGet = [vocabUnit(x) for x in range(unitNr([startUnit[0], 1, 1]), unitNr(currentUnit(date, startUnit, startDate, classType))+1)]
    else:
        unitsToGet = [x for x in listUnits([1,1,1], 127) if x[0] == int(book)]
    unitsToAdd = [x for x in unitsToGet if x not in presentUnits]
    return unitsToAdd
# print(getUnitsToAdd("00104 Arno Bouguennec", [2,11,1], 2))

def acc_report(profileName, rvs, startUnit, classType):
    date=today #dt.date(2022, 2, 15)
    su = list(startUnit)
    startDate = termStart #dt.date(2021, 12, 1)
    cu = list(currentUnit(date, startUnit, startDate, classType))
    chapCompl = anki_db.chapter_completion(profileName, rvs)
    revTime = 30000
    lst = []
    for x in chapCompl:
        uNr = unitNr([x[0][0], x[0][1], 2])
        words = x[1]-x[2]
        if (unitNr(su)<uNr<=unitNr(cu)) and words>0:
            lst.append([x[0], words, anki_db.timeText(words*revTime)])
    if len(lst)==0: return
    return ("acc"+str(lst[-1][0][0])+str(lst[-1][0][1]).zfill(2),
            {"#Chapters": len(lst),
            "#Words": sum([x[1] for x in lst]),
            "time": anki_db.timeText(sum([x[1] for x in lst])*revTime),
            "list": lst})

def audioFileCheck(vocabUnit, numberOfUnits):
    units=listUnits(vocabUnit, numberOfUnits)
    for u in units:
        check = "NOT OK"
        vocLen = len(config_notes.getVu(u)[0].index)
        files=os.listdir(config_notes.getSoundFileDir(u))
        lastFile=files[len(files)-1]
        if int(lastFile.split("_")[3][:2]) == vocLen: check="OK"
        l= [u, len(config_notes.getVu(u)[0].index), lastFile, check]
        print(l)

def example_check(vocabUnit, numberOfUnits):
    units=listUnits(vocabUnit, numberOfUnits)
    result=[]
    for u in units:
        e=0
        for i in config_notes.getVu(u)[0]['Examples']:
            if i: e=e+1
        result.append((u, e))
    return result

 