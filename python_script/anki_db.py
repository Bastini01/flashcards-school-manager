import sqlite3
from os.path import expanduser
from os import listdir, mkdir
import pandas as pd
import numpy as np
from io import StringIO
from html.parser import HTMLParser
import datetime as dt
import math
import config_notes
import re
from shutil import copyfile

today=dt.date.today()
Anki2Dir = expanduser("~")+"\\AppData\\Roaming\\Anki2\\"
technicalFilesPath = expanduser("~")+'\\OneDrive\\SRL\\TechnicalFiles\\'
logPath = technicalFilesPath+r'Log'

def copyAnki2():
    dirList = listdir(Anki2Dir)[:-3]
    c = "\collection.anki2"
    t= technicalFilesPath
    for i in dirList:
        # print(Anki2Dir+i+c)
        # print(t+"\\Anki2copy\\"+i.split("\\")[-1]+c)
        dst = t+"Anki2copy\\"+i.split("\\")[-1]
        try: mkdir(dst) 
        except: pass
        try: copyfile(Anki2Dir+i+c, dst+c)
        except: continue

copyAnki2()

def dbPath(profileName):
    return Anki2Dir+profileName+"\\collection.anki2"

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def unit(txt):
    reg = r'(?:Book.*([1-5])).*(?:Chapter.*([0-1][0-9])).*[^I]([1-2]|I+)'
    # reg = r'Book([1-5])Chapter([0-1][0-9])-([1-2])'
    r=re.search(reg, txt)
    try:
        p=r.group(3)
        if r.group(3)=="I": p="1"
        elif r.group(3)=="II": p="2" 
        return [int(r.group(1)), int(r.group(2)), int(p)]
    except: return None
    # return r.group(0)
# (unit("Book5/Chapter02-II "))
# (unit("Book5Chapter02-2 "))
# (unit("heu???"))

def timeText(time):
    mins=round(time/60000)
    dec=mins/60 % 1
    if mins<2: result = "1 minute"
    elif mins<60:
        result = str(mins)+" minutes"
    elif dec<0.25: 
        result = str(round(mins/60)) +" hour"
        if round(mins/60)>1: result=result+"s"
    elif 0.25<=dec<=0.75: 
        result = str(math.floor(mins/60)) +",5 hours"
    elif dec>0.75: result = str(round(mins/60)) +" hours"

    return result

def queryDb(profileName, query):
    con = sqlite3.connect(dbPath(profileName))
    cursor = con.cursor()
    query = query
    cursor.execute(query)
    result = cursor.fetchall()
    con.close()
    return result

def getReviews(profileName):

    query = "SELECT revlog.*, notes.flds, notes.tags FROM "\
            "(revlog INNER JOIN cards ON revlog.cid=cards.id)"\
            "INNER JOIN notes ON cards.nid = notes.id"\

    reviewst = queryDb(profileName, query)
    #process TradChars date and unit
    reviewsl=[]
    for i in reviewst:
        l=list(i)
        reviewsl.append(l)
        l.append(profileName)
        l.append(l[0])
        try:
            l.append(strip_tags(l[9].split("\x1f")[0]).strip('"'))
            l[9]=strip_tags(l[9].split("\x1f")[3]).strip('"')
            l[9]=HTMLParser().unescape(l[9])      
        except: pass           
        l[0]=dt.datetime.fromtimestamp(round(l[0]/1000.0))
        l[10]= unit(l[10])

    return reviewsl
# getReviews("00016 Jose Loo")

def review_mean_duration(reviews):
    # t=textbook_new_word_review(reviews)['reviewDuration'].mean()
    if len(reviews)==0: return 0
    lst=[x[7] for x in reviews]
    return round(sum(lst)/len(lst)/1000)
# (review_mean_duration(getReviews("00053 Paul H Nemra")))

def pending_learning(profileName):
    query = "SELECT cards.id, MAX(revlog.id), cards.queue, cards.ivl, SUBSTRING(tags, INSTR(tags, 'Book'), 20) FROM "\
            "((cards INNER JOIN revlog ON cards.id=revlog.cid)"\
            "INNER JOIN notes ON cards.nid=notes.id) "\
            "INNER JOIN decks ON cards.did=decks.id "\
            "WHERE tags LIKE '%Book%Chapter%' AND decks.name LIKE '%當代%'"\
            "GROUP BY cards.id"
    qresult = queryDb(profileName, query)
    # ([
    #     [dt.datetime.fromtimestamp(round(i[1]/1000.0)).date(), i[3]]
    #        for i in qresult
    # ])
    drtn=review_mean_duration(getReviews(profileName))
    def chap(x): return (unit(x)[0],unit(x)[1])
    chapters= sorted({chap(i[4]) for i in qresult})
    result={i:[0,0,0] for i in chapters}
    for i in qresult:
        revdate=dt.datetime.fromtimestamp(round(i[1]/1000.0)).date()
        if i[2]==1:
            result[chap(i[4])][1]=result[chap(i[4])][1]+1
            result[chap(i[4])][2]=result[chap(i[4])][2]+drtn
        elif revdate+dt.timedelta(days=i[3])<=today:
            result[chap(i[4])][0]=result[chap(i[4])][0]+1
            result[chap(i[4])][2]=result[chap(i[4])][2]+drtn
    
    for i in result: result[i][2]=timeText(result[i][2]*1000)
    result = [[[x[0], x[1]], result[x][0], result[x][1], result[x][2]] for x in result]
    return result
# (pending_learning("00024 馬修 郭"))

def last_review_date(reviews):
    return max([l[0] for l in reviews]).date()
# (last_review_date(getReviews("00053 Paul H Nemra")))

def rev_to_df(reviews):
    df=pd.DataFrame(reviews, columns=[
        'reviewTime', 
        'cardID', 
        'usn', 
        'buttonPressed', 
        'newInterval', 
        'previousInterval', 
        'newFactor', 
        'reviewDuration', 
        'reviewType', 
        'tradChars',
        'tags', 
        'student',
        'revId',
        'en'])
    return df
# revnem=rev_to_df(getReviews("00017 Ali Watak"))
# revnem.to_csv('Ali_watak.txt')
# dafr=revnem[revnem['tags'] != None]
# dafr=revnem.to_csv('revNemra.txt')

def reviews_by_period(profileName, start=None, end=None):
    try: rev=getReviews(profileName)
    except: return []
    if rev==[]: return []
    if start==None: start=dt.datetime(2021, 1, 1)
    else: start = dt.datetime(start.year, start.month, start.day)
    if end==None: end=dt.datetime(today.year, today.month, today.day)
    else: end = dt.datetime(end.year, end.month, end.day)
    return [i for i in rev if i[0] >= start and i[0] <= end]

def isSerious(threshhold, profileName, start=None, end=None):
    try: cnt=len(reviews_by_period(profileName, start, end))
    except: return False
    if cnt >= threshhold: return True
    else: return False

def topXdifficult(reviews, x=100):
    result=[]
    for i in [1,2]:
        if i==1: timeOrder=True 
        else: timeOrder=False
        rvs = [rev for rev in reviews if rev[10] and rev[3] == i]
        def col(x): return [r[x] for r in rvs]
        df = pd.DataFrame({
            'word': col(9), 
            'chap': [tuple(r[10]) for r in rvs],
            'time': col(7)})
        df=df.groupby(['word', 'chap']).agg({'time':['count', 'sum']}
        ).sort_values(
                    by=[('time', 'count'), ('time', 'sum')], 
                    ascending=[False, timeOrder])

        for row in df.iterrows():
            wc=[row[0][0], row[0][1]]
            if wc not in result and len(result)<x:
                result.append(wc)
                if len(result)==x: return result
    
    return result
# (topXdifficult(getReviews("00048 Nadia 敏 Chang 李"), 10))

def textbook_new_word_review(reviews):
    revs1 = [x for x in reviews if x[10] != None]
    df1 = rev_to_df(revs1)
    df2 = df1.groupby(['en']).revId.agg('min')
    df3 = df1.merge(df2, how='right', on='revId')
    return df3
# (textbook_new_word_review("00007 洋娜 宋"))

def chapter_1st_review(chapter, revs):
    df = textbook_new_word_review(revs)
    df['tags']=df['tags'].apply(lambda x: str([x[0], x[1]]))
    df2 = df[df['tags'] == str(chapter)]
    return df2
# (len(chapter_1st_review([3, 8], "00007 洋娜 宋")))

def cntOfNotes(profileName, vocabUnit):
    tag=config_notes.getVu(vocabUnit)[1]

    query = "SELECT count(notes.id) FROM notes"\
            "WHERE notes.tags==' Book1Chapter09*'"

def getUnits(profileName):

    query = "SELECT MAX(notes.id), SUBSTRING(tags, INSTR(tags, 'Book'), 20), COUNT(notes.id) FROM "\
            "(notes INNER JOIN cards ON notes.id=cards.nid) "\
            "INNER JOIN decks ON cards.did=decks.id "\
            "WHERE tags LIKE '%Book%Chapter%'"\
            "GROUP BY 2"
                         
    units = queryDb(profileName, query)
    # (units)
    unitsl=[]
    for i in units:
        l=list(i)
        l[0]=dt.date.fromtimestamp(round(l[0]/1000.0))
        l[1]=unit(l[1])
        unitsl.append(l)

    return unitsl

def getLastUnit(profileName):
    unitsl = getUnits(profileName)
    if len(unitsl)==0: return None
    else: return unitsl[-1]

def chapter_completion(profileName, revs):
    units = getUnits(profileName)
    chapters = {(tuple(x[1][:-1]),0,0) for x in units}
    result = []
    for i in chapters:
        x=list(i)
        for j in units:
            if (j[1][0], j[1][1])==i[0]: x[1]=x[1]+j[2] 
        if i[0][0]<3: x[1]=int(x[1]/2)
        x[2] = len(chapter_1st_review(list(i[0]), revs))
        result.append(x); result.sort()
    return result

def first_review_completion_report(profileName, revs):
    chapCompl = chapter_completion(profileName, revs)
    complete=[]
    incomplete=[]
    for c in chapCompl:  
        if c[1]==0 or c[1]>200: continue
        if c[2]/c[1]>0.8: complete.append(list(c[0]))
        else: 
            incomplete.append([
                list(c[0]),
                c[1]-c[2],
                round((c[1]-c[2])*review_mean_duration(revs)/60),
                round((1-c[2]/c[1])*100)
            ])
    return complete, incomplete

def periodReport(profileName, reviews, start, end):
    endstr1= end.strftime('%y%m%d')
    periodRvs=[]
    tbWords=[]
    otbWords=[]
    chapters=[]
    time=0
    lastRev=start
    for rev in reviews:
        if start <= rev[0].date() <end:
            periodRvs.append(rev)
            time=time+rev[7]
            if rev[0].date()>lastRev: lastRev=rev[0].date()
            if rev[10]:
                if len(rev[10])>2: rev[10].pop()
                if rev[9] not in tbWords: 
                    tbWords.append(rev[9])
                    if rev[10] not in [x[0] for x in chapters]: chapters.append([rev[10], 1])
                    else: 
                        for i in chapters: 
                            if i[0] == rev[10]: i[1]=i[1]+1
            elif rev[9] not in otbWords: otbWords.append(rev[9])
    chapters.sort()
    top10 = topXdifficult(periodRvs, 10)

    pl=pending_learning(profileName)
    pending = sum([x[1] for x in pl])
    learning = sum([x[2] for x in pl])
    
    return endstr1, {
        'reviews': len(periodRvs),
        'time': timeText(time),
        'hours': math.floor(time/3600000),
        'tbWords': len(tbWords),
        'chaps': len(chapters),
        'otbWords': len(otbWords),
        'top': top10,
        'lastRev': lastRev,
        'chaps-words': chapters,
        'completion': first_review_completion_report(profileName, reviews) if len(periodRvs)>0 else (None, None),
        'pendingLearning': pl,
        'pending': pending,
        'learning': learning
    }

def termReport(termStart, profileName, reviews):
    start= termStart
    end= today
    report=periodReport(profileName, reviews, start, end)
    return 'termReport'+report[0], report[1]
# (termReport(getReviews("00053 Paul H Nemra")))

def month_report(profileName, reviews):
    start = dt.date(today.year, today.month, 1)
    next_month = today.replace(day=28) + dt.timedelta(days=4)
    end =  next_month - dt.timedelta(days=next_month.day)
    report=periodReport(profileName, reviews, start, end)
    return 'month'+report[0][:-2], report[1]

def week_dates():
    start= today-dt.timedelta(days=today.weekday(), weeks=1)
    end= today-dt.timedelta(days=today.weekday())
    return start, end

def weeklyReport(profileName, reviews):
    start= week_dates()[0]
    end= week_dates()[1]
    report=periodReport(profileName, reviews, start, end)
    return 'weekly'+report[0], report[1]
# (weeklyReport("00053 Paul H Nemra", getReviews("00053 Paul H Nemra")))

def weekly_send_conditions(reviews, weekly):
    if(weekly[1]['reviews'] > 1 or(
            weekly[1]['pending'] > 10 or
            weekly[1]['completion'][1]) and 
            weekly[1]['lastRev'] >= last_review_date(reviews)): 
            return True
    else: return False

def dailyReport(profileName, reviews):
    start= today-dt.timedelta(days=1)
    end=today
    r=periodReport(profileName, reviews, start, end)
    chaps=[x[0] for x in r[1]['chaps-words']]
    if not r[1]['completion'][1]: return 'daily'+r[0], r[1]
    for i in r[1]['completion'][1]:
        if i[0] not in chaps: r[1]['completion'][1].remove(i)
    return 'daily'+r[0], r[1]
# dailyReport("00024 馬修 郭", getReviews("00024 馬修 郭"))
# weekly=weeklyReport("00102 Sven Riebesam", getReviews("00102 Sven Riebesam"))
# (weekly)
# daily=dailyReport("00017 Ali Watak", getReviews("00017 Ali Watak"))
# (daily)

