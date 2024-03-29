from os.path import expanduser, join, getmtime
import numpy as np
from numpy import NaN, count_nonzero
import re
import pandas as pd
import pdfkit
import anki_db as db
import config_notes, mtc_info, AllReviews
import datetime as dt
import class_stats, mtc_info
import google_apps as g
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import PercentFormatter
from matplotlib.dates import DateFormatter
import json
import webbrowser

dfst = g.getStudents()

today = dt.datetime.now().date()
statsPath = join(db.technicalFilesPath, "stats\\")

capstyle = {'selector': 'caption', 'props': [('text-align', 'left'), ('font-size', '150%'), ('font-weight', 'bold')]}
tablestyle = {'selector':'', 'props':[('table-layout','fixed'), ('text-align','center'), ]}
tabelAttr = 'style="white-space: nowrap; table-layout: auto; width: 110%"'
statsRoot = '/autoflashcards/run/stats/'

def d_2_str(x): 
    return dt.datetime.combine(
        x, dt.datetime.min.time()).strftime('%y%m%d')

def classOverview(): #number of active users by class

    df1=g.st_cl_te(mtc_info.get_term(today)['term'])
    df1['serious']=df1.apply(lambda x: db.isSerious(150, x['profileName']), axis=1)
    df1['state']=df1['state'].apply(lambda x: x[:-1] if x[:3]=="con" else x)
    df1.loc[df1.serious==True, 'state']='active'
    df1=df1.set_index(['state', 'serious', 'type', 'name', 'class_id'], append=True)
    df2=df1['profileName']
    df2=df2.unstack(['type', 'name', 'class_id'])
    df2=df2.reset_index(level=0, drop=True)
    df2.sort_index(inplace=True, ascending=[True, False])
    df2.sort_index(axis='columns', inplace=True)
    df3=df2.groupby(['state', 'serious']).agg('count')
    old_idx = df3.index.to_frame()
    old_idx.insert(2, 'group', ['count' for x in range(len(df3))])
    df3.index = pd.MultiIndex.from_frame(old_idx)
    for i in range(len(df3)):
        n=df3.iloc[i].name
        df3.loc[(n[0], n[1], '%')]= df3.iloc[i]/df3[:3].sum(axis=0)*100
    df3.sort_index(inplace=True, ascending=[True, False, True])
    df3.to_html(join(statsPath,'classOverview.html'))
    return df3
# classOverview().to_html(db.technicalFilesPath + 'testest.html')
# webbrowser.open(db.technicalFilesPath + 'testest.html')


def print_class_reports(term = None):
    path = statsPath+r'class_reports'
    trm = mtc_info.get_term(today)['term'] if not term else term
    c=g.getData()['class']
    df=c[c['term']==trm]
    st_cl_te = g.st_cl_te(trm)
    for row in df.iterrows():
        print(row[1][0])       
        rep=class_stats.class_report(row[1][0], False, st_cl_te)[1]
        if not rep['styler']: continue
        rep['styler'].to_html(
            join(path,
            rep['class']+
            rep['teacherName']+
            '.html'))

def str_to_unit(x):
    rgx = re.compile("([0-9]), ([0-9]+), ([1-2])")
    return [int(rgx.search(x)[i]) for i in range(1, 4)]

def voc_analysis_base(r):
    df = r[r['tags'].notnull()] 
    df = df[df['student']!='00239 Tenzin Topden']
    # df = df[df['tags'].apply(lambda x: x[0] < 6)]
    df['TextbookChapter'] = df['tags'].apply(lambda x: str(x))
    # print(df[df['TextbookChapter']=="[7, 1, 1]"])
    return df

def voc_analysis_grpby_student(r): #input allReviews
    df = voc_analysis_base(r)
    df = df.groupby(['tradChars', 'TextbookChapter', 'student']).agg(
        難度=('buttonPressed','mean'),
        複習次數=('cardID','count')).reset_index()
    df['難度'] = df['難度'].apply(lambda x: round(10-(x-1)*(10/3), 1))
    return df

def voc_analysis(r, min=None, max=None, chapter=None, round=False):
    df = voc_analysis_grpby_student(r)
    df = df.groupby(['tradChars', 'TextbookChapter']).agg(
        count=('student', 'count'), 
        mean=('難度','mean')
        ).reset_index()
    df['count'] = df['count'].round(decimals=0).astype(object)
    if round: df['mean'] = df['mean'].round(decimals=1).astype(object)

    if chapter == None: voc = config_notes.getVocSource()
    else:
        voc1 = config_notes.getVu([chapter[0], chapter[1], 1])[0]
        voc2 = config_notes.getVu([chapter[0], chapter[1], 2])[0]
        voc = pd.concat([voc1, voc2])
    voc['TextbookChapter'] = voc['TextbookChapter'].apply(lambda x: str(db.unit(x)))
    voc = voc[voc['TextbookChapter'].apply(lambda x: str_to_unit(x)[0] < 6)]
    df = df.rename(columns={'tradChars':'Traditional Characters'})   
    df=voc.merge(df, how='left', on=['Traditional Characters', 'TextbookChapter'])
    if min:
        df = df[df['TextbookChapter'].apply(lambda x: mtc_info.unitNr(str_to_unit(x))>=mtc_info.unitNr(min))]
    if max:
        df = df[df['TextbookChapter'].apply(lambda x: mtc_info.unitNr(str_to_unit(x))<mtc_info.unitNr(max))]
    return df[['TextbookChapter', 'Traditional Characters', 'count', 'mean']]

def word_students(r, chap, word, min=None, max=None):
    def click(x): 
        b = '<a href='+statsRoot+'word/{chap}/{word}/{x}>{x}</a>'
        return b.format(chap=str(chap[0])+'-'+str(chap[1]), word=word.encode('punycode'), x=x)
    df = voc_analysis_grpby_student(r)
    df = df[df['TextbookChapter'].apply(lambda x: str(str_to_unit(x)[:-1])) == str(chap)]
    df = df[df['tradChars'] == word]
    df = df.drop(['TextbookChapter', 'tradChars'], axis=1
        ).sort_values('複習次數', ascending=False)    
    df['student'] = df['student'].apply(lambda x: dfst[dfst['profileName']==x]['studentId'].values[0])
    df['student'] = df['student'].apply(click)
    tablestyle = {'selector':'', 'props':[('table-layout','fixed')]}
    tabelAttr = 'style="white-space: nowrap; table-layout: auto; width: 400px; text-align: center; font-size:calc(5px + 1vw)"'

    stlr = df.style.format(precision=1).background_gradient(cmap='RdYlGn_r', subset='難度', vmin=1, vmax=7
            ).hide(axis='index').set_caption(
                '用APP複習過 "'+word+'" 的學生'
            ).set_table_styles([capstyle, tablestyle], overwrite=False
            ).set_table_attributes(tabelAttr)
    return stlr

def charfbutton(b):
    if b == 1: return "忘記"
    elif b == 2: return "很難"
    elif b == 3: return "OK"
    elif b == 4: return "容易"

def button_color(b): #hide NaN values
    attr = 'color: %s'
    if b[0] == "忘記": return [attr % 'red']
    elif b[0] == "很難": return [attr % 'orange']
    elif b[0] == "OK": return [attr % 'green']
    elif b[0] == "容易": return [attr % 'blue']


def student_word(r, chap, word, sid, min=None, max=None):
    df = voc_analysis_base(r)
    df = df[df['TextbookChapter'].apply(lambda x: str(str_to_unit(x)[:-1])) == str(chap)]
    df = df[df['tradChars'] == word]
    df['student'] = df['student'].apply(lambda x: dfst[dfst['profileName']==x]['studentId'].values[0])
    df = df[df['student'] == sid]
    df = df[['reviewTime', 'buttonPressed']].rename(columns={'reviewTime': '複習時間', 'buttonPressed': '答案'}
            ).sort_values('複習時間', ascending=False)
    df['答案'] = df['答案'].apply(charfbutton)
    tablestyle = {'selector':'', 'props':[('table-layout','fixed')]}
    tabelAttr = 'style="white-space: nowrap; table-layout: auto; width: 400px; text-align: center; font-size:calc(5px + 1vw)"'
    caption = """<a href={root}student/{sid}/all>{sid}</a> 學號: 
              "<a href={root}word/{chap}/{wordc}/all/all>{word}</a>" 複習次序""" 
    stlr = df.style.format(precision=1).hide(axis='index').set_caption(
            caption.format(root = statsRoot, sid=sid, word = word,
                chap=str(chap[0])+"-"+str(chap[1]), 
                wordc = word.encode('punycode'))
            ).set_table_styles([capstyle, tablestyle], overwrite=False
            ).set_table_attributes(tabelAttr).apply(button_color, axis=1, subset='答案'
            )
    return stlr
# print(student_word(AllReviews.getReviewDataAll(), [1, 3], "音樂", "220361127"))
# student_word(AllReviews.getReviewDataAll(), [1, 3], "音樂", "220361127").to_html(db.technicalFilesPath + 'testest.html')
# webbrowser.open(db.technicalFilesPath + 'testest.html')


def voc_analysis_excel():
    terms=['all', '21winter', '22spring', '22summer']
    AllReviews.getReviewDataAll().to_csv(db.technicalFilesPath+'all_reviews.txt')
    for x in terms:
        voc_analysis(AllReviews.getReviewDataAll(x)).to_csv(db.technicalFilesPath+'voc_analysis_'+x+'.txt')

def highlight_max(data): #hide NaN values
        attr = 'background-color: {}'.format('white') +'; color: %s' % 'white'
        if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
            is_max = data == 0
            return [attr if v else '' for v in is_max]
        else:  # from .apply(axis=None)
            is_max = data == 0
            return pd.DataFrame(np.where(is_max, attr, ''),
                                index=data.index, columns=data.columns)

def vertical_border(data):
    return ['border-right: 1px solid' for n in data]

def voc_analysis_html(r, term='all', min=None, max=None, click=False, showNumbers=False):
    df = voc_analysis(r, min, max)
    df['TextbookChapter'] = df['TextbookChapter'].apply(
        lambda x: str(str_to_unit(x)[0])+" 册 "+str(str_to_unit(x)[1]))
    df = df.rename(columns={'Traditional Characters':'生詞',
                'count': '人數', 'mean': '難度'})
    dfr = pd.DataFrame()
    chaps = df['TextbookChapter'].unique()
    meanCols = []
    tradCols = []
    for i in chaps:
        dfi = df[df['TextbookChapter']==i].drop('TextbookChapter', axis=1).reset_index(drop=True)
        dfi.columns = pd.MultiIndex.from_tuples([(i, x) for x in dfi.columns.values])
        if not dfi[dfi.columns.values[1]].isnull().all():
            dfi = dfi.sort_values((i, '難度'), ascending=False).reset_index(drop=True)
            dfr = pd.concat([dfr, dfi], axis=1)
            meanCols.append((i,'難度')); tradCols.append((i,'生詞')) 

    if click: 
        dfr[tradCols] = dfr[tradCols].apply(
            lambda x: x+"x"+x.name[0][0]+"-"+x.name[0][4:])

    dfr = dfr.fillna(0)

    spacing = {(n[0],'生詞'):[{'selector':'','props':[('padding-left', '20px'), ("border-left", "1px solid")]}] for n in meanCols}

    stlr = dfr.style.format(precision=1, na_rep=''
            ).hide(axis='index').set_caption(
                "「MTC 自動化字卡」計畫 ------ 當代中文詞彙圖 ------ "+d_2_str(today)+" 更新"
            ).set_table_styles([capstyle, tablestyle], overwrite=False
            ).set_table_attributes(tabelAttr)

    if click:
        def clck(x):
            if x==0: return ''
            if click=='w': r = 'all/'+term
            elif click[0]=='s': r = click[1:]
            else: b = r = click[1:]+'/'+term
            b = '<a style="text-decoration: none; color: inherit; font-weight: bold" href='+statsRoot+'word/{ch}/{cw}/{r}>{w}</a>'
            return b.format(ch=x.split("x")[1], cw=x.split("x")[0].encode('punycode'), w=x.split("x")[0], r=r)

        stlr = stlr.format(clck, subset=tradCols, na_rep='')


    for i in meanCols:
        stlr = stlr.background_gradient(
            # gmap=dfr[i], axis=0,  cmap='RdYlGn_r', subset=[(i[0],'生詞'), (i[0], '人數'), i], vmin=1, vmax=7)
            gmap=dfr[i], axis=0,  cmap='RdYlGn_r', subset=[(i[0],'生詞')], vmin=1, vmax=7)


    stlr = stlr.apply(highlight_max, axis=None).apply(vertical_border, axis='columns', subset=meanCols)

    if not showNumbers:
        stlr = stlr.hide(subset=meanCols+[(i[0], '人數') for i in meanCols], axis='columns'
            ).hide_columns(level=1)
    
    else:
        tabelAttrx = 'style="white-space: nowrap; max-width: 3508px;"'
        stlr = stlr.set_table_attributes(tabelAttrx)

    return stlr

def voc_analysis_pdf(r=None):
    if not r: r=AllReviews.getReviewDataAll()
    pgs = [[1, 1, 1], [1, 13, 1], [2, 11, 1]]
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    for i in range(len(pgs)-1):
        voc_analysis_html(r, min=pgs[i], max=pgs[1+i], showNumbers=True).to_html(statsPath+'voc_analysis_'+str(i)+'.html')

    pdfkit.from_file([statsPath+'voc_analysis_'+str(i)+'.html' for i in range(len(pgs)-1)], statsPath+'voc_analysis.pdf', 
        options={'orientation': 'landscape', 'encoding': 'UTF-8', 'zoom': 1}, 
        configuration=config)

def reviews_mm(mmx=30):
    df = AllReviews.getReviewDataAll()
    df = df.groupby([df['reviewTime'].dt.date, 'student']).agg({'cardID':'count'}).reset_index()
    def mmXdays(x):
        dft = df[df['student']==x['student']]
        dft = dft[(dft['reviewTime']>=x['reviewTime']-dt.timedelta(days=mmx)) &
            (dft['reviewTime']<=x['reviewTime'])]
        return dft.cardID.sum()/mmx
    df['MMXdays'] = df.apply(mmXdays, 1)
    df = df.rename(columns={'student':'profileName'})
    return df

def total_active(x=5, mm=30): #total number of users who reached an average of more than x reviews/day during at least one month
    df = reviews_mm(mm)
    return len(df[(df['MMXdays']>x)]['profileName'].unique())

def retention(cutoff=None, recent=None): #number of users historically active and number of them no recently active
    cutoff = cutoff if cutoff else 0
    recent = recent if recent else 90
    df = reviews_mm()
    before = df[(df['MMXdays']>cutoff) & (df['reviewTime']<today-dt.timedelta(days=recent))]['profileName'].unique()
    recently = df[df['reviewTime']>today-dt.timedelta(days=recent)]['profileName'].unique()
    retention = [x for x in before if x not in recently]
    return {'before': len(before), 'retention': str(int(100-len(retention)/len(before)*100))+" %"}

def retention_detail():
    # windows = [30, 60, 90]
    windows = [(today-mtc_info.get_term_dates('21winter')['termEnd']).days]
    cols = pd.MultiIndex.from_product([windows, ['nr active', 'retention']])
    df = pd.DataFrame(columns=cols , index=[5, 10, 20]
            ).rename_axis(index='average reviews/day min. threshold', columns=['look back window', 'user cnt'])
    def appfunc(x):
        r = []
        for i in x.index.values:
            if x.name[1]==df.columns.levels[1][1]: n = 'before'
            else: n = 'retention'
            r.append(retention(i, int(x.name[0]))[n])
        return r
    df = df.apply(appfunc, result_type='broadcast')
    return df

def user_distribution(param = None):
    df = AllReviews.getReviewDataAll()
    if not param:
        func = lambda x: x.count()/(dt.datetime.now()-x.min()).days
        lbl = 'reviews/day - all time mean'; lim = [0,40]
    else:
        func = lambda x: x.dt.date.nunique()/(dt.datetime.now()-x.min()).days
        lbl = 'study frequency (days studied/total days active)'; lim = [0,0.95]
    df = df.groupby('student').agg(param = ('reviewTime', func)).reset_index()
    plt.hist(df['param'], bins=1000, cumulative=True, density=True, histtype='step', orientation='vertical')
    plt.xlim(lim)
    plt.ylim([0,1])
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.gca().set_ylabel('cumulative percentange of active users')
    plt.gca().set_xlabel(lbl)
    plt.gca().set_title('MTC Automated flashcards\nactive user analysis')
    plt.gca().invert_yaxis()
    return plt

def periodical_users(period=None, cutoff=None, allReviews = None):
    df = allReviews if type(allReviews)==pd.DataFrame else AllReviews.getReviewDataAll()
    def termDate(x):
        r = mtc_info.get_term(x.date())['termStart'] + dt.timedelta(days=45)
        return dt.datetime.combine(r, dt.datetime.min.time())
    if period=='w': 
        df['reviewTime'] = df['reviewTime'].apply(lambda x: x + dt.timedelta(days=6 - x.weekday()))
    elif period=='m': 
        df['reviewTime'] = df['reviewTime'].apply(lambda x: x.replace(day=15))
    elif period=='term': 
        df['reviewTime'] = df['reviewTime'].apply(termDate)
    df = df.groupby([df['reviewTime'].dt.date, 'student']).agg(
        {'cardID':'count', 
        'reviewDuration':lambda x: sum(x)/60000}
        ).reset_index()
    if period: 
        df['mn rev/day'] = df['cardID'].apply(lambda x: x/7 if period=='w' else x/30, 1)
        if cutoff: df = df[df['mn rev/day']>cutoff]
    elif cutoff: df = df[df['cardID']>cutoff]    
    df = df.groupby([df['reviewTime']]).agg(
        totalRevCount=('cardID','sum'), 
        activeUserCount=('student','nunique'),
        revsMn=('cardID','mean'),
        studytimeMn=('reviewDuration', 'mean')
        )[:-1].astype('int32')
    return df

def trendWeekly(allReviews = None):
    df = periodical_users('w', 5, allReviews).rename(columns={
        'totalRevCount':'總共複習次數',
        'activeUserCount':'使用者人數',
        'revsMn':'平均複習次數',
        'studytimeMn':'平均複習時間'
    }).rename_axis('禮拜')
    df = df.set_axis(
        [d_2_str(x) for x in df.axes[0].values])
    return df

def active_users(totalReviews = 30, term = None): # to be replaced by mm30
    dates = (None, None)
    if term: 
        dts = mtc_info.get_term_dates(term)
        dates = (dts['termStart'], dts['termEnd'])
    df=g.getStudents()
    df = df[['profileName', 'os']]
    df['revs']=df.apply(lambda x: len(db.getReviews(x['profileName'], dates[0], dates[1])), axis=1)
    df['serious']=df.apply(lambda x: True if x['revs']>=totalReviews else False, axis=1)
    df=df[df['serious'] == True]
    return df

def active_user_os():
    df=active_users(term = mtc_info.get_term(today)['term'])
    df = df[['os', 'revs']]
    df = df.groupby(['os']).agg(['count', 'mean'])
    print(df)

def active_users_analysis():
    for i in [50, 100, 500, 1000]:
        print(i,len(active_users(i)))

def save_g_data():
    g.getStudents().to_pickle(db.technicalFilesPath+'studentsDF.pkl')
    g.getEmailLog().to_pickle(db.technicalFilesPath+'emailsLogDF.pkl')

def line_stats(): #registrations based on line csv export - obsolete
    df = pd.read_csv(db.technicalFilesPath+'line_stats.csv')
    df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
    df['contacts'] = df['contacts'].apply(lambda x: x-df['contacts'].min())
    df = df.rename(columns={'contacts':'registrations'})
    return df

def line_follow_date(lineLog):
    # df = g.get_line_log()
    def line_event(x): 
        x = json.loads(json.loads(x)['postData']['contents'])['events']
        return x[0] if len(x)>0 else None
    df = lineLog['full'].apply(line_event)
    df = df[df.notnull()]
    # df = df.loc[lambda x: x['type'] == 'follow']
    df1 = pd.DataFrame()
    df1['type'] = df.apply(lambda x: x['type'])
    df1['regDate'] = df.apply(lambda x: dt.datetime.fromtimestamp(x['timestamp']/1000).date())
    df1['source'] = df.apply(lambda x: x['source'])
    df1 = df1[df1['type'] == 'follow']
    df1['Line ID'] = df1['source'].apply(lambda x: x['userId'])
    # df1 = df1[df1['type'] == 'follow']
    df1 = df1.groupby('Line ID', as_index=False).agg({'regDate':'min'})
    return df1
# (line_follow_date(g.get_line_log()))

def clean_state(x):
    if type(x) == float: return True
    elif x[0] == 'tOut': return True
    elif x[0] == 't': return False
    else: return True

def activation_mail_date(emailLog): #first activation date by student from emailLog
    df = emailLog[emailLog['emailTemplate'] == 'activated_template']
    df = df.groupby('recipientId', as_index=False).agg(activDate=('date','min'))
    df = df.rename(columns={'recipientId':'studentId'})
    return df

def  messaging_analysis(emailLog):
    # df = emailLog[emailLog['type'] == 'gmail']
    df = emailLog[emailLog['emailTemplate'].apply(lambda x: x[:2] == 'cw')]
    df['date'] = df['date'].apply(lambda x: x.replace(day=1))
    df = df.groupby('date', as_index=False).agg('count')
    print(df)
    print(df['type'].sum())
# messaging_analysis(g.getEmailLog())

def student_activation_date(getStudents, emailLog): #combine mail loc and status date for historic activations
    df2 = activation_mail_date(emailLog)
    df = getStudents.merge(df2, how='left', on='studentId')
    df['activDate'] = df['activDate'].apply(lambda x: x['statusDate'] if not x and x['state']=='active' else x)
    df = df[df.activDate.notnull()]
    df = df.groupby('profileName', as_index=False).agg({'activDate':'min'})
    return df

def follow_date(s, e, l): #combine line log and status date for historic registrations and correct with activation date
    df = s.merge(line_follow_date(l), how='left', on='Line ID')
    df = df.merge(student_activation_date(s, e), how='left', on='profileName')
    def func(x):
        r = x['regDate']
        if type(r) == float: r = g.str_2_d(x['Timestamp'])
        if type(x['activDate']) != float: r = min(r, x['activDate'])
        return r
    df['regDate'] = df.apply(func, 1)
    df = df[(df.regDate.notnull() & df['state'].apply(clean_state))]
    df = df.groupby(['profileName', 'state']).agg({'regDate':'min'}).reset_index()
    return df

def regs_by_date(s, e, l):
    df = follow_date(s, e, l)
    df = df.groupby('regDate').agg(regs=('profileName', 'count')).reset_index()
    df['regs'] = df['regs'].cumsum()
    return df
# print(regs_by_date(g.getStudents(), g.get_line_log()))

def activation(getStudents, emailLog): #activations by date
    df = student_activation_date(getStudents, emailLog)
    df = df.groupby('activDate', as_index=False).agg({'profileName':'count'})
    df = df.rename(columns={'profileName' :'activations'})
    df['activations'] = df['activations'].cumsum()
    return df
# (activation(g.getStudents(), g.getEmailLog()))

def activation_analysis(s, e, l):
    mm30 = reviews_mm()
    cutoff = 5
    mm30cut = mm30[mm30['MMXdays']>cutoff].rename(columns={'reviewTime': 'mm30Time'})
    df = follow_date(s, e, l).merge(student_activation_date(s, e), how='left', on='profileName')
    df = df.merge(mm30, how='left', on='profileName')
    df = df.merge(mm30cut, how='left', on='profileName')
    df = df.groupby(['profileName','state', 'regDate', 'activDate'], dropna=False
        ).agg(minRev=('reviewTime', 'min'),
            minCutoff=('mm30Time', 'min')).reset_index()
    # df = df[df['state'].apply(clean_state)]
    def activ_delay(x, param):
        if type(x[param]) != dt.date: return NaN
        else: return (x[param]-x['regDate']).days 
    df['activation delay'] = df.apply(lambda x: activ_delay(x, 'activDate'), 1)
    df['1st rev delay'] = df.apply(lambda x: activ_delay(x, 'minRev'), 1)
    df['reach threshhold delay'] = df.apply(lambda x: activ_delay(x, 'minCutoff'), 1)
    return df
# print(activation_analysis(g.getStudents(), g.getEmailLog(), g.get_line_log()))

def delays_analysis(s, e, l):
    df = activation_analysis(s, e, l)
    l=[['activation delay', 'Account activation delay'],
        ['1st rev delay', 'Delay between line follow and 1st review'],
        ['reach threshhold delay','Delay between line follow and reaching activity threshold']]
    for i in l:
        df1 = df[df[i[0]].notnull()][i[0]]
        plt.hist(df1, bins=1000, cumulative=True, label=i[1],
            density=True, histtype='step', orientation='vertical')
    plt.gca().set_title('MTC Automated flashcards\ndelay analysis')
    plt.xlim([0, 40])
    plt.gca().set_xlabel('Days')
    plt.gca().legend()
    plt.ylim([0,1])
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.gca().set_ylabel('Cumulative percentange of active users')    
    plt.gca().invert_yaxis()
    return plt

def activation_funnel(s, e, l, term='all'):
    d1 = activation_analysis(s, e, l)
    minDate = d1['regDate'].min() if term=='all' else mtc_info.get_term_dates(term)['termStart']
    maxDate = today if term=='all' else mtc_info.get_term_dates(term)['termEnd']
    d1 = d1[d1['regDate']>=minDate]
    d1 = d1[d1['regDate']<=maxDate]
    df = {}; tot = len(d1)
    def state_not_reg(x):
        if type(x) == float: return False
        elif x[:-1] == 'reg': return False
        else: return True
    df.update({"registered": round(len(d1[d1['state'].apply(state_not_reg)])/tot*100)})
    df.update({"activated": round(len(d1[d1['state'] == 'active'])/tot*100)})
    df.update({"1 rev": round(len(d1[d1['minRev'] <= maxDate])/tot*100)})
    df.update({"active user": round(len(d1[d1['minCutoff'] <= maxDate])/tot*100)})
    
    x_pos = np.arange(len(df))
    plt.bar(x_pos, df.values())
    plt.xticks(x_pos, df.keys())
    plt.ylim([0,100])
    plt.gca().set_ylabel('users %')
    
    # ax.legend()
    title = "activation funnel - total users: "+str(tot)+"\n Period: "
    if term: title += term
    else: title += d_2_str(minDate) +" - "+d_2_str(maxDate)
    plt.title(title)
    return plt
    
def plot_user_trend(s, e, l, period=None, cutoff=None):
    # dr = line_stats()
    # plt.xticks(rotation=70)

    dr = regs_by_date(s, e, l)
    da = activation(s, e)
    ax = plt.subplots()[1]
    ax.plot(dr.regDate, dr.regs, linewidth=2, label='registered')
    ax.plot(da.activDate, da.activations, linewidth=2, label='activated')
    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative number of students')
    ax.set_title('MTC Automated flashcards user trend')
    dfu = periodical_users(period, cutoff).activeUserCount
    ax2 = ax.twinx()
    
    if period:
        if period == "w": labelr = 'weekly unique users' 
        elif period == "m": labelr = 'monthly unique users'
        else: labelr = 'unique users per term'
    else:       
        x = 7; dfu = dfu.rolling(window=x).mean()
        labelr = "daily unique users ("+str(x)+" day MM)"
        
    ax2.plot(dfu.index, dfu.values, 'g', linestyle='dotted')       
    ax2.set_ylabel(labelr+"\n(min "+str(cutoff)+" reviews/day on average)", color='g') 
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    # myFmt = DateFormatter('%m-%Y')
    # ax.xaxis.set_major_formatter(myFmt)
    # for label in ax.get_xticklabels():
    #     label.set_rotation(40)
    return plt

def update_stats():
    s = g.getStudents()
    e = g.getEmailLog()
    l = g.get_line_log()
    r = AllReviews.getReviewDataAll()
    cutoff = 5
    recent = 90
    # for term in ['all','21winter', '22spring', '22summer']:
    #     activation_funnel(s, e, l, term).savefig(statsPath+"act_funnel_"+term+".png", bbox_inches='tight')
    #     plt.gcf().clear()
    # delays_analysis(s, e, l).savefig(statsPath+"delays analysis.png", bbox_inches='tight')
    # plt.gcf().clear()
    plot_user_trend(s, e, l, None, cutoff).savefig(statsPath+"user trend day.png", bbox_inches='tight')
    print("user trend day ok"); plt.gcf().clear()
    plot_user_trend(s, e, l, 'w', cutoff).savefig(statsPath+"user trend week.png", bbox_inches='tight')
    print("user trend week ok"); plt.gcf().clear()
    plot_user_trend(s, e, l, 'm', cutoff).savefig(statsPath+"user trend month.png", bbox_inches='tight')
    print("user trend month ok"); plt.gcf().clear()
    plot_user_trend(s, e, l, 'term', cutoff).savefig(statsPath+"user trend term.png", bbox_inches='tight')
    print("user trend term ok"); plt.gcf().clear()
    # user_distribution().savefig(statsPath+"user analysis mean.png", bbox_inches='tight')
    # print("user mean rev ok"); plt.gcf().clear()
    # user_distribution('f').savefig(statsPath+"user analysis frequency.png", bbox_inches='tight')
    # print("user freq ok"); plt.gcf().clear()
    # retention_detail().style.to_html(statsPath+'Retention analysis.html')
    # voc_analysis(r, round=True).to_csv(join(statsPath,'vocAnalysis.txt'))
    # voc_analysis_pdf(r)




