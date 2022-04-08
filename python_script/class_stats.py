import pandas as pd
import anki_db as db
from mtc_info import unit_to_zh, get_current_term
import traceback

# import google_apps as g
# gStudent=g.getStudents()
# gData=g.getData()
# gClass=gData['class']
# gs_c=gData['student_class']
# gTeacher=gData['teacher']

def st_cl_te(gStudent, gClass, gs_c, gTeacher, trm = None):
    term=get_current_term()['term'] if not trm else trm
    stud=gStudent
    c=gClass
    s_c=gs_c
    t=gTeacher
    df=stud.merge(s_c, how='left', on='studentId')
    df=df.merge(c, how='left', on='class_id')
    df1=df.merge(t, how='left', on='teacher_id')
    df1=df1[df1['term']==term]
    return df1
# sct = st_cl_te(gStudent, gClass, gs_c, gTeacher)#.to_excel("st_cl_te.xlsx")

def class_type(profileName, st_cl_te):
    df=st_cl_te[st_cl_te['profileName']==profileName]
    if len(df) == 0: return None
    classType = df.iloc[0].at['type']
    if not classType: return None
    else: return int(classType)

def start_unit(profileName, st_cl_te):
    df=st_cl_te[st_cl_te['profileName']==profileName]
    if len(df) == 0: return None
    else:
        su=df.iloc[0].at['startUnit']
        startUnit=[int(su.split(",")[0]), int(su.split(",")[1]), 1] if su else None 
        return startUnit

def class_report(st_cl_te, class_id, period='term'):
    df=st_cl_te
    df=df[df['class_id']==class_id]
    if len(df)==0: return 'classWeekly', {'empty': True, 'styler': None}
    teacherId = df.iloc[0, df.columns.get_loc("teacher_id")]
    teacherName = df.iloc[0, df.columns.get_loc("name")]
    teacherEmail = df.iloc[0, df.columns.get_loc("email")]
    df = df[['studentId','profileName']]
    per = db.week_dates() if period == 'week' else db.term_dates()
    timeFrame = per[0].strftime('%Y/%m/%d')+" - "+per[1].strftime('%Y/%m/%d')

    def report(x):
        try:
            if period == 'week': return db.weeklyReport(x, db.getReviews(x))
            else: return db.termReport(x, db.getReviews(x))
        except Exception as e: 
            tb = traceback.format_exc(limit=50)
            print("class report student error: ", class_id, x, teacherId, tb, e)
            return (None, {'chaps-words': [], 'top': []})

    df['本期複習的課'] = df.apply(
        lambda x: report(x['profileName'])[1]['chaps-words'], 
        axis=1)
    df['最常被忘記的生詞'] = df.apply(
        lambda x: report(x['profileName'])[1]['top'][:6], 
        axis=1)

    df= df[df["最常被忘記的生詞"].str.len() != 0]
    df.reset_index(drop=True, inplace=True)
    df['最常被忘記的生詞'] = df['最常被忘記的生詞'].apply(lambda x: [i[0] for i in x])
    df.rename(columns={'studentId': '學號', 'profileName': '名字'}, inplace=True)
    df['名字']=df['名字'].apply(lambda x: x[5:])
    def chap_name(x): 
        return [unit_to_zh(i[0]) for i in x if i[1]>2] 
    def list_to_text(x):
        txt=''
        for i in x: txt=txt+i+", "
        return txt[:-2]
    df["本期複習的課"]=df["本期複習的課"].apply(lambda x: chap_name(x))
    df["本期複習的課"]=df["本期複習的課"].apply(lambda x: list_to_text(x))
    df["最常被忘記的生詞"]=df["最常被忘記的生詞"].apply(lambda x: list_to_text(x))
    stlr = df.style.set_caption("班: "+class_id+" --- 老師: "+teacherName+" --- 期間: "+timeFrame)
    htmlReport = stlr.to_html()
    return 'classWeekly',{
        'class': class_id,
        'teacherId': teacherId,
        'teacherName': teacherName,
        'teacherEmail': teacherEmail,
        'timeFrame': timeFrame,
        'empty': True if len(df)==0 else False,
        'styler':stlr,
        'htmlReport':htmlReport
    }
# rep = class_report(sct, '41875', 'week')
# # rep=class_report('41661')
# # # rep['report'].to_excel(rep['class']+rep['teacherName']+'.xlsx')
# # rep[1]['htmlReport'].style.to_html(rep[1]['class']+rep[1]['teacherName']+'.html')
# logFilePath=rep[1]['class']+rep[1]['teacherName']+'.html'
# logFile = open(logFilePath,'w', encoding="utf-8")
# logFile.write(rep[1]['htmlReport'])
# logFile.close()


# gClass.apply(lambda x: print(x['class_id'], x['teacher_id']), axis=1)

