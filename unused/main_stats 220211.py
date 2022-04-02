import pandas as pd
import anki_db as db
import config_notes, mtc_info, AllReviews
import datetime as dt
import class_stats


def classOverview():

    df1=class_stats.st_cl_te()
    df1['serious']=df1.apply(lambda x: db.isSerious(30, x['profileName']), axis=1)
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
    # roll_up tentative for sidplaying student name/number
    # df3=pd.DataFrame(columns=df2.columns, index=df2.index)
    # for i in range(len(df2)):
    #     for j in range(len(df2.columns)):
    #         e1=df2.iloc[i, j]
    #         if pd.isna(e1) == False: 
    #             for k in range(len(df3)):
    #                 e2=df3.iat[k,j]
    #                 if pd.isna(e2) == True: 
    #                     df3.iat[k,j]=e1
    #                     break
    #             else: df3.loc[k+1,df3.columns[j]]=e1 
    
    return df3
# print(classOverview())
# classOverview().to_excel('class_list.xlsx')

def print_class_reports():
    c=class_stats.gClass
    df=c[c['term']=='21winter']
    for row in df.iterrows():
        print(row[1][0])
        rep=class_stats.class_report(row[1][0])
        rep['report'].to_html(
            rep['class']+
            rep['teacherName']+
            # rep['timeFrame']+
            '.html')
# print_class_reports() 

def vocAnalysis(reviews, chapter=None):
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
    df['mean']=round((df['mean']-1)*3.33, 1)
    return df
# vocAnalysis(pd.read_pickle('allReviews.pkl')).to_csv("vocAnalysis.txt")

# def voc_analysis_to_pdf():
#     path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
#     config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)
#     vocAnalysis=pd.read_pickle('vocAnalysi.pkl')
#     # revs=AllReviews.getReviewDataAll()
#     units=mtc_info.listUnits([1,1,1], 127)
#     chapters=[]
#     for i in units:
#         c=[i[0], i[1]]
#         if c not in  chapters: chapters.append(c)
#     print([str(i) for i in chapters])
#     html='<meta http-equiv="Content-type" content="text/html; charset=utf-8" />'
    
#     # page=[[],[]]
#     # for c in chapters:
#     #     chap=vocAnalysis[
#     #         vocAnalysis.index.isin([str(c)],
#     #         level='TextbookChapter')
#     #         ].to_html()
#     #     if len(page[0]) < 4:
#     #         page[0].append(chap)
#     #     elif len(page[1]) < 4:
#     #         page[1].append(chap)
#     #     else:
#     #         html=html+"<html><body>"+tabulate(page, tablefmt='html')
#     #         page=[[chap],[]]
#     # html=html+tabulate(page, tablefmt='html')

#     for c in chapters:
#         chap=vocAnalysis[
#             vocAnalysis.index.isin([str(c)],
#             level='TextbookChapter')
#             ]
#         styler = chap.style.set_table_attributes("style='display:inline'")
#         # styler = chap.style.set_properties(**{
#         #     'font-size': '5pt'
#         #         })
#         # html=html+styler._repr_html_()
#         html=html+styler.to_html()
#     pdf.from_string(html, "pdftest.pdf", configuration=config)
#     # chap=vocAnalysis[
#     #         vocAnalysis.index.isin(['[1, 14]'],
#     #         level='TextbookChapter')
#     #         ].to_html()
#     # pdf.from_string(html, "pdftest2.pdf", configuration=config)
#     print(html)
#     # print(html)

def trendWeekly(allReviews): #still soms issues
    allReviews=allReviews[allReviews['reviewTime'] >= dt.datetime(2021, 12, 1)]
    # for i in range(len(allReviews)):
    #     allReviews.loc[i,'年'] = allReviews.loc[i,'reviewTime'].isocalendar().year
    #     allReviews.loc[i,'week'] = allReviews.loc[i,'reviewTime'].week
    allReviews['年'] = allReviews.apply(lambda x: x['reviewTime'].isocalendar().year, axis=1)
    allReviews['week'] = allReviews.apply(lambda x: x['reviewTime'].week, axis=1)
    df=allReviews.groupby(['年', 'week', 'student']).agg(revs=('cardID', 'count'), studTime=('reviewDuration', 'sum'))
    df.reset_index(level=2, inplace=True)
    df['serious']=df.apply(lambda x: db.isSerious(30, x['student']), axis=1)
    df=df[df['serious'] == True]

    ################# display serious and note serious distinction
    # ind=df.index.tolist()
    # for i in range(len(df)):
    #     l=list(ind[i])
    #     if df.loc[df.index[i],'cardID']>30: l.insert(3, 'serious')
    #     else: l.insert(3, 'not serious')
    #     ind[i]=tuple(l)
    # nind=pd.Index(data=ind, name=('year', 'month', 'week', 'type', 'student'),  tupleize_cols=True)
    # df.set_index(nind, inplace=True)

    df['studTime']=df.studTime/60000
    
    # df=df.groupby(['week']).agg(
    #     {'cardID': ['sum','count'],
    #     'avgWeeklyReviews': 'mean',
    #     'avgWeeklyTime(min)': 'mean'})
    df=df.groupby(['年', 'week']).agg(
        總共複習次數=('revs','sum'), 
        使用者人數=('student','count'),
        平均複習次數=('revs','mean'),
        平均複習時間=('studTime', 'mean'))
    df=df.astype('int32')

    # fig, ax = plt.subplots()

    # # hide axes
    # fig.patch.set_visible(False)
    # ax.axis('off')
    # ax.axis('tight')
    # ax.table(cellText=df.values, colLabels=df.columns, loc='center')

    # fig.tight_layout()

    # plt.show()
    # #https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
    # fig, ax =plt.subplots(figsize=(12,4))
    # ax.axis('tight')
    # ax.axis('off')
    # the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')

    # # #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
    # pp = PdfPages("foo.pdf")
    # pp.savefig(fig, bbox_inches='tight')
    # pp.close()
    return df
# trendWeekly(AllReviews.getReviewDataAll()).to_excel('weekly_trend.xlsx')

def chapter_1st_review(chapter, profileName):
    revs = db.getReviews(profileName)
    # print(revs)
    # print([x[10] for x in revs])
    revs1 = [x for x in revs if x[10] != None and [x[10][0], x[10][1]] == chapter]
    # print(len(revs1))
    df = db.rev_to_df(revs1)
    # print(df.head())
    df = df.groupby(['tradChars']).reviewTime.agg('min')
    print()
    revs2 = [x for x in revs1 if x[0] in df.values.tolist()]
    print(len(revs2))
    return df
# print(chapter_1st_review([1, 8], "00053 Paul H Nemra"))

def chapter_completion(chapter, profileName):
    return