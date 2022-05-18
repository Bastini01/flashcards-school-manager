from os.path import expanduser, join
import pandas as pd
import anki_db as db
import config_notes, mtc_info, AllReviews
import datetime as dt
import class_stats, mtc_info, main
import google_apps as g

# studData=g.getStudents()
# emailLog=g.getEmailLog()
# gData=g.getData()
# gClass=gData['class']
# gs_c=gData['student_class']
# gTeacher=gData['teacher']

# st_cl_te = class_stats.st_cl_te(studData, gClass, gs_c, gTeacher, '22spring')

# st_cl_te.to_excel('st_cl_te.xlsx')

def classOverview():

    df1=st_cl_te
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
    df3=df3.astype('int32')
    
    return df3

def print_class_reports(term = None):
    trm = mtc_info.get_current_term()['term'] if not term else term
    c=gClass
    df=c[c['term']==trm]
    for row in df.iterrows():
        print(row[1][0])
        rep=class_stats.class_report(st_cl_te, row[1][0])[1]
        rep['styler'].to_html(
            rep['class']+
            rep['teacherName']+
            # rep['timeFrame']+
            '.html')
# print_class_reports('21winter') 

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
        # else: reviews.loc[i,'tags'] = str(r) 
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
    df.to_csv(join(main.technicalFilesPath,'vocAnalysis.txt'))
    return

def trendWeekly(allReviews):
    # allReviews = AllReviews.getReviewDataAll()
    filterdf=allReviews[allReviews['reviewTime'] < dt.datetime(2021, 12, 1)]
    allReviews.drop(index=filterdf.index, inplace=True)
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
    filePath=join(main.logPath,"weekly_trend"+dt.datetime.now().strftime('%y%m%d%H%M')+".txt")
    df.to_csv(filePath)
    return df
# trendWeekly(AllReviews.getReviewDataAll()).to_excel('weekly_trend'+dt.datetime.now().strftime('%y%m%d%H%M')+'.xlsx')
