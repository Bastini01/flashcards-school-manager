from os.path import expanduser, join, getmtime
import pandas as pd
import anki_db as db
import config_notes, mtc_info, AllReviews
import datetime as dt
import class_stats, mtc_info
import google_apps as g
import matplotlib.pyplot as plt

def classOverview():

    df1=g.st_cl_te(mtc_info.get_current_term()['term'])
    df1['serious']=df1.apply(lambda x: db.isSerious(150, x['profileName']), axis=1)
    df1['state']=df1['state'].apply(lambda x: x[:-1] if x[:3]=="con" else x)
    # df1['state']=df1.apply(lambda x: 'active' if x['serious']=="active" else x['state'])
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
    # df3=df3.astype('int32')
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

def periodical_users(param=None):
    df = AllReviews.getReviewDataAll()
    if param=='w': 
        df['reviewTime'] = df['reviewTime'].apply(lambda x: x + dt.timedelta(days=7 - x.weekday()))
    elif param=='m': 
        df['reviewTime'] = df['reviewTime'].apply(lambda x: x.replace(day=15))
    df = df.groupby([df['reviewTime'].dt.date])['student'].nunique()[:-1]
    return df
# (periodical_users('w'))

def trendWeekly(allReviews = None):
    revspath = db.technicalFilesPath+'allReviews.pkl'
    if allReviews: allReviews = allReviews
    elif getmtime(revspath) > dt.datetime.now().replace(second=0, hour=0, minute=0).timestamp():       
        allReviews = pd.read_pickle(revspath)
    else: allReviews = AllReviews.getReviewDataAll()
    # filterdf=allReviews[allReviews['reviewTime'] < dt.datetime(2021, 11, 1)]
    # allReviews.drop(index=filterdf.index, inplace=True)
    allReviews['年'] = allReviews.apply(lambda x: x['reviewTime'].isocalendar().year, axis=1)  
    allReviews['week'] = allReviews.apply(lambda x: x['reviewTime'].week, axis=1)
    df=allReviews.groupby(['年', 'week', 'student']).agg(revs=('cardID', 'count'), studTime=('reviewDuration', 'sum'))
    df.reset_index(level=2, inplace=True)
    df['serious']=df.apply(lambda x: db.isSerious(30, x['student']), axis=1)
    df=df[df['serious'] == True]
    df['studTime']=df.studTime/60000
    
    df=df.groupby(['年', 'week']).agg(
        總共複習次數=('revs','sum'), 
        使用者人數=('student','count'),
        平均複習次數=('revs','mean'),
        平均複習時間=('studTime', 'mean'))
    df=df.astype('int32')
    #####SEND MAIL
    stlr = df.style.set_caption("WEEKLY TREND")
    htmlReport = stlr.to_html()
    g.sendActions([{"emailTemplate":('statsReport', htmlReport)}])
    filePath=join(db.logPath,"weekly_trend"+dt.datetime.now().strftime('%y%m%d%H%M')+".txt")
    df.to_csv(filePath)
    return df
# trendWeekly()

def active_users(totalReviews = 30, term = None):
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
# (active_users(totalReviews = 30, term = "22summer"))

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
# save_g_data()

def activation():
    # df1 = g.getStudents()
    # df2 = g.getEmailLog()
    df1 = pd.read_pickle(db.technicalFilesPath+'studentsDF.pkl')
    df2 = pd.read_pickle(db.technicalFilesPath+'emailsLogDF.pkl')
    df2 = df2[df2['emailTemplate'] == 'activated_template']
    df2 = df2.groupby('recipientId', as_index=False).agg({'date':'min'})
    df2 = df2.rename(columns={'recipientId':'studentId'})
    df = df1.merge(df2, how='left', on='studentId')
    df['date'] = df['date'].apply(lambda x: x['statusDate'] if not x and x['state']=='active' else x)
    df = df[df.date.notnull()]
    df = df.groupby('studentId', as_index=False).agg({'date':'min'})
    df = df.groupby('date', as_index=False).agg({'studentId':'count'})
    df = df.rename(columns={'studentId' :'activations'})
    df['activations'] = df['activations'].cumsum()
    return df
# activation()    

def line_stats():
    df = pd.read_csv(db.technicalFilesPath+'line_stats.csv')
    df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
    df['contacts'] = df['contacts'].apply(lambda x: x-df['contacts'].min())
    df = df.rename(columns={'contacts':'registrations'})
    return df

def registration_activation_compare(param=None):
    dr = line_stats()
    da = activation()
    ax = plt.subplots()[1]
    ax.plot(dr.date, dr.registrations, linewidth=2, label='registered')
    ax.plot(da.date, da.activations, linewidth=2, label='activated')
    ax.set_xlabel('time')
    ax.set_ylabel('cumulative')
    ax.set_title('MTC Automated flashcards user trend')
    dfu = periodical_users(param)
    ax2 = ax.twinx()
    
    if param:
        labelr = 'weekly unique users' if param == "w" else 'monthly unique users'
    else:       
        x = 7; dfu = dfu.rolling(window=x).mean()
        labelr = "daily unique users ("+str(x)+" day MM)"
        
    ax2.plot(dfu.index, dfu.values, 'g', linestyle='dotted')       
    ax2.set_ylabel(labelr, color='g') 
    ax.legend()
    plt.show()

# registration_activation_compare('m')