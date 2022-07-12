from cgi import MiniFieldStorage
from os.path import expanduser, join, getmtime
import numpy as np
from numpy import NaN
import pandas as pd
import anki_db as db
import config_notes, mtc_info, AllReviews
import datetime as dt
import class_stats, mtc_info
import google_apps as g
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import json

today = dt.datetime.now().date()

def classOverview():

    df1=g.st_cl_te(mtc_info.get_current_term()['term'])
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
    df3.to_html(join(db.technicalFilesPath,'classOverview.html'))
    return df3

def print_class_reports(term = None):
    path = db.technicalFilesPath+r'class_reports'
    trm = mtc_info.get_current_term()['term'] if not term else term
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

def vocAnalysis(chapter=None):
    reviews = AllReviews.getReviewDataAll()
    if chapter == None: voc = config_notes.getVocSource()
    else:
        voc1 = config_notes.getVu([chapter[0], chapter[1], 1])[0]
        voc2 = config_notes.getVu([chapter[0], chapter[1], 2])[0]
        voc = pd.concat([voc1, voc2])
    for i in range(len(voc)): 
        voc.loc[i,'TextbookChapter'] = str(db.unit(voc.loc[i,'TextbookChapter'])[:-1])
    for i in range(len(reviews)): 
        r=reviews.loc[i,'tags']
        if r: reviews.loc[i,'tags'] = str(r[:-1])   
    df=voc.merge(
        reviews, 
        how='left', 
        left_on=['Traditional Characters', 'TextbookChapter'],
        right_on=['tradChars', 'tags'])
    df=df.groupby([
        'TextbookChapter',
        'Traditional Characters', 
        'student']
        ).buttonPressed.agg('mean')
    df=df.groupby(['TextbookChapter','Traditional Characters']).agg(['count', 'mean'])
    df['mean']=round(10-(df['mean']-1)*(10/3), 1)
    df.to_csv(join(db.technicalFilesPath,'vocAnalysis.txt'))
    return

def reviews_mm30():
    df = AllReviews.getReviewDataAll()
    df = df.groupby([df['reviewTime'].dt.date, 'student']).agg({'cardID':'count'}).reset_index()
    def mm30days(x):
        dft = df[df['student']==x['student']]
        dft = dft[(dft['reviewTime']>=x['reviewTime']-dt.timedelta(days=30)) &
            (dft['reviewTime']<=x['reviewTime'])]
        return dft.cardID.sum()/30
    df['MM30days'] = df.apply(mm30days, 1)
    df = df.rename(columns={'student':'profileName'})
    return df
# print(reviews_mm30())

def hookoffs(cutoff=None, recent=None):
    cutoff = cutoff if cutoff else 0
    recent = recent if recent else 90
    df = reviews_mm30()
    before = df[(df['MM30days']>cutoff) & (df['reviewTime']<today-dt.timedelta(days=recent))]['profileName'].unique()
    recently = df[df['reviewTime']>today-dt.timedelta(days=recent)]['profileName'].unique()
    hookoffs = [x for x in before if x not in recently]
    # print(str(len(before))+" users have reached at least "+str(cutoff)+" "\
    #     "reviews per day on average on a period of 30 days, at some point more than "+str(recent)+" days ago. "\
    #     +str(len(hookoffs))+" of these users have not reviewed in the last "+str(recent)+" days.")
    return {'before': len(before), 'hookoffs': len(hookoffs)}

def hookoffs_detail():
    # df = pd.DataFrame(['historically active', 'not active recently'],{'cutoff': [0, 1, 5, 10, 20], 'recent': [30, 60, 90]})
    cols = pd.MultiIndex.from_product([[30, 60, 90], ['were active', 'quit']])
    df = pd.DataFrame(columns=cols , index=[0, 1, 5, 10, 20]
            ).rename_axis(index='average reviews/day min. threshold', columns=['look back window', 'user cnt'])

    def appfunc(x):
        r = []
        for i in x.index.values:
            if x.name[1]==df.columns.levels[1][1]: n = 'before'
            else: n = 'hookoffs'
            r.append(hookoffs(i, int(x.name[0]))[n])
            # r.append(str(i)+str(x.name)+n)
        return r

    df = df.apply(appfunc, result_type='broadcast')
    df.style.to_html(db.technicalFilesPath+'Quit anaysis.html')
    print(df)
# hookoffs_detail()

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
    #plt.show()
    return plt

def periodical_users(period=None, cutoff=None, allReviews = None):
    df = allReviews if type(allReviews)==pd.DataFrame else AllReviews.getReviewDataAll()
    if period=='w': 
        df['reviewTime'] = df['reviewTime'].apply(lambda x: x + dt.timedelta(days=6 - x.weekday()))
    elif period=='m': 
        df['reviewTime'] = df['reviewTime'].apply(lambda x: x.replace(day=15))
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
        [dt.datetime.combine(x, dt.datetime.min.time()
        ).strftime('%y%m%d') for x in df.axes[0].values]
    )
    #####SEND MAIL
    stlr = df.style.set_caption("WEEKLY TREND")
    htmlReport = stlr.to_html()
    g.sendActions([{"emailTemplate":('statsReport', htmlReport)}])
    # filePath=join(db.logPath,"weekly_trend"+dt.datetime.now().strftime('%y%m%d%H%M')+".txt")
    # df.to_csv(filePath)
    print(df)

def active_users(totalReviews = 30, term = None): #obsolete
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
    df=active_users(term = mtc_info.get_current_term()['term'])
    df = df[['os', 'revs']]
    df = df.groupby(['os']).agg(['count', 'mean'])
    print(df)

def active_users_analysis():
    for i in [50, 100, 500, 1000]:
        print(i,len(active_users(i)))

def save_g_data():
    g.getStudents().to_pickle(db.technicalFilesPath+'studentsDF.pkl')
    g.getEmailLog().to_pickle(db.technicalFilesPath+'emailsLogDF.pkl')

def line_follow_date():
    df = g.get_line_log()

    def line_event(x): 
        x = json.loads(json.loads(x)['postData']['contents'])['events']
        return x[0] if len(x)>0 else None
    df = df['full'].apply(line_event)
    df = df[df.notnull()]
    df1 = pd.DataFrame()
    df1['type'] = df.apply(lambda x: x['type'])
    df1['followDate'] = df.apply(lambda x: dt.datetime.fromtimestamp(x['timestamp']/1000).date())
    df1['Line ID'] = df.apply(lambda x: x['source']['userId'])
    df1 = df1[df1['type'] == 'follow']
    df1 = df1.groupby('Line ID', as_index=False).agg({'followDate':'min'})
    # df1 = df1[df1['dateTime']>dt.datetime(2022,5,1)]

    # print(df1)
    return df1

# print(line_follow_date())

def student_activation_date(): #first activation date by student
    df = g.getEmailLog()
    # df = pd.read_pickle(db.technicalFilesPath+'emailsLogDF.pkl')
    df = df[df['emailTemplate'] == 'activated_template']
    df = df.groupby('recipientId', as_index=False).agg(activDate=('date','min'))
    df = df.rename(columns={'recipientId':'studentId'})
    return df

def activation_analysis1():
    mm30 = reviews_mm30()
    cutoff = 5
    mm30cut = mm30[mm30['MM30days']>cutoff].rename(columns={'reviewTime': 'mm30Time'})

    dfs = g.getStudents()
    df = line_follow_date().merge(dfs, how='left', on='Line ID')
    df = df.merge(student_activation_date(), how='left', on='studentId')
    df = df.merge(mm30, how='left', on='profileName')
    df = df.merge(mm30cut, how='left', on='profileName')
    # df = df.groupby(['Line ID', 'state', 'dateTime', 'date']
    df = df.groupby(['Line ID', 'state', 'followDate', 'activDate'], dropna=False
        ).agg(minRev=('reviewTime', 'min'),
            minCutoff=('mm30Time', 'min')).reset_index()
    def func1(x):
        if type(x) == float: return True
        elif x[0] == 't': return False
        else: return True
    df = df[df['state'].apply(func1)]
    # df = df[df['state'].apply(lambda x: type(x)) == float]
    def activ_delay(x, param):
        if type(x[param]) != dt.date: return NaN
        else: return (x[param]-x['followDate']).days 
    df['activation delay'] = df.apply(lambda x: activ_delay(x, 'activDate'), 1)
    df['1st rev delay'] = df.apply(lambda x: activ_delay(x, 'minRev'), 1)
    df['reach threshhold delay'] = df.apply(lambda x: activ_delay(x, 'minCutoff'), 1)
    # df = df[df['followDate']>=dt.date(2022,5,1)]
    # df['state'] = df['state'].apply(lambda x: x[:-1])
    # df = df.groupby('state').agg({'Line ID':'nunique'})

    # df['percentage'] = df['Line ID'].apply(lambda x: round(x/df['Line ID'].sum(),2))
    # print(df)
    return df
# activation_analysis1()

def delays_analysis(param = None):
    df = activation_analysis1()
    if param == 'activation delay':
        lbl = 'account activation delay'; lim = [0,40]
    elif param == '1st rev delay':
        lbl = 'delay between line follow and 1st review'; lim = [0,40]
    else:
        lbl = 'delay between line follow and reaching activity threshold'; lim = [0,40]
    df = df[df[param].notnull()][param]
    plt.hist(df, bins=1000, cumulative=True, density=True, histtype='step', orientation='vertical')
    plt.xlim(lim)
    plt.ylim([0,1])
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.gca().set_ylabel('cumulative percentange of active users')
    plt.gca().set_xlabel(lbl)
    plt.gca().set_title('MTC Automated flashcards\ndelay analysis')
    plt.gca().invert_yaxis()
    plt.show()
    return plt
    # print(df)
# delays_analysis('activation delay')
# delays_analysis('1st rev delay')
# delays_analysis('reach threshhold delay')

def activation_funnel():
    d1 = activation_analysis1()
    # minDate = 
    # maxDate = 
    # d1 = d1[d1['followDate']>=minDate]
    # d1 = d1[d1['followDate']<=maxDate]
    # d1 = d1[d1['followDate']<dt.date(2022,6,15)]
    # d1 = d1[d1['followDate']<=d1['followDate'].min()+dt.timedelta(days=30)]
    df = {}
    tot = len(d1)
    # df.update({"Line Follow": tot})
    def func1(x):
        if type(x) == float: return False
        elif x[:-1] == 'reg': return False
        else: return True
    df.update({"registered": round(len(d1[d1['state'].apply(func1)])/tot, 2)})
    df.update({"activated": round(len(d1[d1['state'] == 'active'])/tot, 2)})
    df.update({"1 rev": round(len(d1[d1['minRev'].notnull()])/tot, 2)})
    df.update({"active user": round(len(d1[d1['minCutoff'].notnull()])/tot, 2)})
    # df.update({"registered": len(d1[d1['state'].apply(func1)])})
    # df.update({"activated": len(d1[d1['state'] == 'active'])})
    # df.update({"1 rev": len(d1[d1['minRev'].notnull()])})
    # df.update({"active user": len(d1[d1['minCutoff'].notnull()])})
    x_pos = np.arange(len(df))
    print(df.keys(), df.values())
    # Create bars
    plt.bar(x_pos, df.values())

    # Create names on the x-axis
    plt.xticks(x_pos, df.keys())

    # ax.set_ylabel('users %')
    # ax.set_title('MTC Automated flashcards activation funnel')
    
    # ax.legend()
    plt.title("activation funnel - total users: "+str(tot)+"\n")
    plt.show()

    # print(df)
activation_funnel()

def activation(): #combine mail loc and status date for historic activations
    df1 = g.getStudents()
    # df1 = pd.read_pickle(db.technicalFilesPath+'studentsDF.pkl')
    df2 = student_activation_date()
    df = df1.merge(df2, how='left', on='studentId')
    df['activDate'] = df['activDate'].apply(lambda x: x['statusDate'] if not x and x['state']=='active' else x)
    df = df[df.date.notnull()]
    df = df.groupby('studentId', as_index=False).agg({'activeDate':'min'})
    df = df.groupby('activDate', as_index=False).agg({'studentId':'count'})
    df = df.rename(columns={'studentId' :'activations'})
    df['activations'] = df['activations'].cumsum()
    return df

def line_stats():
    df = pd.read_csv(db.technicalFilesPath+'line_stats.csv')
    df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
    df['contacts'] = df['contacts'].apply(lambda x: x-df['contacts'].min())
    df = df.rename(columns={'contacts':'registrations'})
    return df

def plot_user_trend(period=None, cutoff=None):
    dr = line_stats()
    da = activation()
    ax = plt.subplots()[1]
    ax.plot(dr.date, dr.registrations, linewidth=2, label='registered')
    ax.plot(da.date, da.activations, linewidth=2, label='activated')
    ax.set_xlabel('time')
    ax.set_ylabel('cumulative')
    ax.set_title('MTC Automated flashcards user trend')
    dfu = periodical_users(period, cutoff).activeUserCount
    ax2 = ax.twinx()
    
    if period:
        labelr = 'weekly unique users' if period == "w" else 'monthly unique users'
    else:       
        x = 7; dfu = dfu.rolling(window=x).mean()
        labelr = "daily unique users ("+str(x)+" day MM)"
        
    ax2.plot(dfu.index, dfu.values, 'g', linestyle='dotted')       
    ax2.set_ylabel(labelr+"\n(less than "+str(cutoff)+" reviews/day on average not counted)", color='g') 
    ax.legend()
    #plt.show()
    return plt

def runAllStats():
    
    cutoff = 0
    recent = 90
    # plot_user_trend(None, cutoff).savefig(db.technicalFilesPath+"user trend day.png", bbox_inches='tight')
    # print("user trend day ok"); plt.gcf().clear()
    plot_user_trend('w', cutoff).savefig(db.technicalFilesPath+"user trend week.png", bbox_inches='tight')
    print("user trend week ok"); plt.gcf().clear()
    # plot_user_trend('m', cutoff).savefig(db.technicalFilesPath+"user trend month.png", bbox_inches='tight')
    # print("user trend month ok"); plt.gcf().clear()
    # user_distribution().savefig(db.technicalFilesPath+"user analysis mean.png", bbox_inches='tight')
    # print("user mean rev ok"); plt.gcf().clear()
    # user_distribution('f').savefig(db.technicalFilesPath+"user analysis frequency.png", bbox_inches='tight')
    # print("user freq ok"); plt.gcf().clear()
    # hookoffs(cutoff, recent)
# runAllStats()






