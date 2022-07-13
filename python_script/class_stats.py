import anki_db as db
from mtc_info import unit_to_zh, get_term_dates
import google_apps as g
import traceback

def class_report(class_id, week=False, st_cl_te = None):
    df=st_cl_te if st_cl_te is not None else g.st_cl_te()
    df=df[df['class_id']==class_id]
    if len(df)==0: return 'classWeekly', {'empty': True, 'styler': None}
    teacherId = df.iloc[0, df.columns.get_loc("teacher_id")]
    teacherName = df.iloc[0, df.columns.get_loc("name")]
    teacherEmail = df.iloc[0, df.columns.get_loc("email")]
    term = df.iloc[0, df.columns.get_loc("term")]
    df = df[['studentId','profileName']]
    per = db.week_dates() if week else (get_term_dates(term)['termStart'], get_term_dates(term)['termEnd'])
    timeFrame = per[0].strftime('%Y/%m/%d')+" - "+per[1].strftime('%Y/%m/%d')

    def report(x):
        try:
            if week: return db.weeklyReport(x, db.getReviews(x))
            else: return db.termReport(per[0], x, db.getReviews(x))
        except Exception as e: 
            tb = traceback.format_exc(limit=50)
            print("class report student error: ", class_id, x, teacherId, tb, e)
            return (None, {'chaps-words': [], 'top': []})

    df['本期複習的課'] = df.apply(
        lambda x: report(x['profileName'])[1]['chaps-words'], axis=1)
    df['最常被忘記的生詞'] = df.apply(
        lambda x: report(x['profileName'])[1]['top'][:6], axis=1)

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