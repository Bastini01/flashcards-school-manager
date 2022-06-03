import numpy as np
import datetime as dt
import math
import anki_db
import os
import config_notes

termStartUnits=[[1,1,1],[1,6,1],[2,1,1],[2,6,1],[2,11,1],[3,9,1],[4,1,1]]

def dateList(sdate, edate):
    return [sdate+dt.timedelta(days=x) for x in range((edate-sdate).days)]

now=dt.datetime.now()
today=now.date()

businessDaysPerTerm=47 #actually 57, tweaked to match the actual speed of progress

 ####x days sooner to accomodate early registrations
fallDate=[9, 1]
winterDate=[12, 1]
springDate=[3, 5] #2 
summerDate=[6, 6] #1
########
nyDec = dt.date( today.year, 12, 31 )
nyJan = [dt.date( today.year, 1, 1 ), dt.date( today.year, 1, 2 )]
cny = dateList(dt.date( today.year, 1, 29 ), dt.date( today.year, 2, 7))
springBreak = dateList(dt.date( today.year, 4, 1 ), dt.date( today.year, 4, 7))
midAtumn = dt.date( today.year, 9, 9 )
doubleTen = dt.date( today.year, 10, 10 )

bdc=np.busdaycalendar(holidays=[*nyJan, *cny, *springBreak, midAtumn, doubleTen, nyDec])

def get_current_term():
    if today.month==12:
        termStart= dt.date( today.year, winterDate[0], winterDate[1])
        termEnd= dt.date( today.year+1, springDate[0], springDate[1])
        term=str(termStart.year)[2:]+"winter"
    elif today.month< 3 or today.month==3 and today.day< springDate[1]:
        termStart= dt.date( today.year-1, winterDate[0], winterDate[1])
        termEnd= dt.date( today.year, springDate[0], springDate[1])
        term=str(termStart.year)[2:]+"winter"
    elif today < dt.date( today.year, summerDate[0],summerDate[1]):
        termStart= dt.date( today.year, springDate[0], springDate[1])
        termEnd= dt.date( today.year, summerDate[0],summerDate[1])
        term=str(termStart.year)[2:]+"spring"
    elif today < dt.date( today.year, fallDate[0],fallDate[1]):
        termStart= dt.date( today.year, summerDate[0], summerDate[1])
        termEnd= dt.date( today.year, fallDate[0],fallDate[1])
        term=str(termStart.year)[2:]+"summer"
    else: 
        termStart= dt.date( today.year, fallDate[0], fallDate[1])
        termEnd= dt.date( winterDate[0], winterDate[1])
        term=str(termStart.year)[2:]+"fall"
    return {'term': term, 'termStart': termStart, 'termEnd': termEnd}

termStart = get_current_term()['termStart']

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
#print(nextUnit([3,10,2]))

def unitAhead(vocabUnit, numberOfUnits=None):
    vu=vocabUnit
    if not numberOfUnits: return nextUnit(vu)

    for i in range(numberOfUnits):
        vu=nextUnit(vu)
    return vu
# print(unitAhead([2,8,1], 1))

def listUnits(vocabUnit, numberOfUnits): #list of units ahead
    vu=vocabUnit
    l=[list(vocabUnit)]
    for i in range(numberOfUnits+1):
        if i==0: continue
        l.append(list(nextUnit(vu)))
    return l

def vocabUnit(unitNr):
    return listUnits([1,1,1], 127)[unitNr]
# print(vocabUnit(60))

def unitNr(vocabUnit):
    return listUnits([1,1,1], 127).index(vocabUnit)
# print(unitNr([3,1,1]))

def countAllUnits():
    unit=[1,1,1]
    x=0
    for i in range(1000):
        if unit==[5,10,2]:
            return x
        x=x+1
        unit=unitAhead(unit)
# print(countAllUnits())

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
    # print(tsu)
#termStartUnit([3,10,1])      

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
# print(addDays([1,6,1],2))

def addDatesTerm(startUnit, classType): #####deprecated
    addDates=[]
    x=0
    for d in dateList(termStart, termStart+dt.timedelta(days=100)):
        bd=np.busday_count(termStart, d, busdaycal=bdc)
        isbd=np.is_busday(d, busdaycal=bdc)
        print(d,bd, isbd)
        if (bd in addDays(startUnit, classType)) and isbd==True:
                x=x+1
                #print(d, x)
                addDates.append(d)
    return addDates

def addDatesCustom(startUnit, startDate, classType):
    dl=dateList(startDate, startDate+dt.timedelta(days=100))
    bdl=[dl[i] for i in range(len(dl)) if np.is_busday(dl[i], busdaycal=bdc)]
    units = addDays(startUnit, classType)
    return [[bdl[u[0]], u[1]] for u in units] 
# print(addDatesCustom([1,6,1], dt.date( 2021, 12, 1 ), 2))

def pAddDatesRandA(startUnit): #####deprecated
    l=[]
    for i in range(len(addDatesTerm(startUnit, 1))):
        r= addDatesTerm(startUnit, 2)[i] if i < len(addDatesTerm(startUnit, 2)) else None
        l.append([str(addDatesTerm(startUnit, 1)[i]),str(r)])
    for i in l:
        print(i)
# pAddDatesRandA([1, 1, 1])

def currentUnit(date, startUnit, startDate, classType):
    du=addDatesCustom(startUnit, startDate, classType)
    for i in du:
        if i[0]<=date:
            u=i[1]
    return u
# print(unitNr(currentUnit(today, [1,6,1], dt.date( 2021, 12, 1 ), 2)))

def getUnitsToAddOld(profileName, startUnit, classType): 
    #to do: change logic: compare 'to have' units with 'already have' units and add difference
    # to avoid first units missing due to wrong 'satrt unit' entry 
    date=today
    startDate = termStart
    lastUnit= anki_db.getLastUnit(profileName)
    lastUnitNr= unitNr(lastUnit[1]) if lastUnit else unitNr(startUnit)-1
    cuNr= unitNr(currentUnit(date, startUnit, startDate, classType))
    n=cuNr-lastUnitNr
    if n>0:
        unitsToAdd=listUnits(vocabUnit(lastUnitNr+1), n-1)
    else: unitsToAdd=[]
    return unitsToAdd

def getUnitsToAdd(profileName, startUnit=None, classType=None, book=None): 
    date=today
    startDate = termStart
    presentUnits = [x[1] for x in anki_db.getUnits(profileName)]
    if not book:
        unitsToGet = [vocabUnit(x) for x in range(unitNr([startUnit[0], 1, 1]), unitNr(currentUnit(date, startUnit, startDate, classType)))]
    else:
        unitsToGet = [x for x in listUnits([1,1,1], 127) if x[0] == int(book)]
    unitsToAdd = [x for x in unitsToGet if x not in presentUnits]
    return unitsToAdd


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
#(acc_report("00053 Paul H Nemra", anki_db.getReviews("00053 Paul H Nemra"), [1,6,1], 2))

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
# audioFileCheck([2, 1, 1], 29)

def example_check(vocabUnit, numberOfUnits):
    units=listUnits(vocabUnit, numberOfUnits)
    result=[]
    for u in units:
        e=0
        for i in config_notes.getVu(u)[0]['Examples']:
            if i: e=e+1
        result.append((u, e))
    return result
# lst=[x[1] for x in example_check([1,1,1], 29)]
# print(lst)
# print(sum(lst)/len(lst)) 

 