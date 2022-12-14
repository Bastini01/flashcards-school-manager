from flask import json
from werkzeug.exceptions import HTTPException

from posixpath import split
import time, re, pandas as pd
from flask import Flask, render_template, request, redirect, flash
from threading import Thread
import main, main_stats, AllReviews, google_apps as g
import class_stats
import config_notes as nts

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q2z\n\xec]/'
app.debug = True
allTerms = ['21winter', '22spring', '22summer', '22fall', '22winter', 'all']
def click_class(x): return '<a href='+main_stats.statsRoot+'class/'+x+'>'+x+'</a>'


class PrefixMiddleware(object):
#class for URL sorting 
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        #in this line I'm doing a replace of the word flaskredirect which is my app name in IIS to ensure proper URL redirect
        if environ['PATH_INFO'].lower().replace('/autoflashcards','').startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'].lower().replace('/autoflashcards','')[len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])            
            return ["This url does not belong to the app.".encode()]


app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/run')

class Compute(Thread):
    def __init__(self, setting):
        Thread.__init__(self)
        self.setting = setting

    def run(self):
        if self.setting[:2] == 'st':
            main.main(idFilter = self.setting[2:])
        if self.setting[:4] == 'book':
            main.add_book(sId = self.setting[4:-1], book = self.setting[-1:])
        elif self.setting == 'all':
            main.main(std=True) 

@app.errorhandler(HTTPException)
def handle_exception(e):
    # return e.get_response()
    return render_template("500_generic.html", e=e), 500

@app.route('/stats/voc/<term>')
def run_stats_voc(term):
    r = AllReviews.getReviewDataAll(term)
    message = 'Table insert'
    terms = list(allTerms); terms.remove(term)
    table = main_stats.voc_analysis_html(r, term, click='w').to_html()
    temp = render_template('voctable.html', table=message, terms=terms, term=term)
    temp = temp.replace('Table insert', table)
    return temp

@app.route('/stats/word/<chap>/<word>/<clss>/<term>')
def run_stats_word(chap, word, clss, term):
    r = AllReviews.getReviewDataAll(term)
    st = g.getStudents()
    gd = g.getData()
    df1 = g.st_cl_te(studData = st, gData = gd)
    terms = list(allTerms); terms.remove(term)
    if clss != 'all':
        df = df1[df1['class_id']==clss]
        studList = df['profileName'].unique()
        r = r[r['student'].apply(lambda x: x in studList)]
    word = bytes(word[2: -1], 'utf8').decode('punycode')
    chap = [int(chap.split('-')[0]), int(chap.split('-')[1])]
    df = nts.getVocSource()
    df = nts.chap_filter(df, chap)
    picSrc = nts.pic_url(df, chap, word)
    df = df[df['Traditional Characters'] == word]
    eng = df['Definition (en)'].values[0]
    py = df['PinYin'].values[0]
    ex = df['Examples'].values[0].replace("_x000D_", "")
    table = main_stats.word_students(r, chap, word)
    if clss != 'all': table.caption = "班號 "+clss+": "+table.caption
    try: table = table.to_html()
    except: table = "此班("+clss+")此學季("+term+")沒學生複習過"
    temp = render_template('word.html', 
        tradChar=word, eng=eng, PinYin=py, exSentence=ex, picSrc=picSrc,
        term=term, terms=terms)
    temp = temp.replace('Table insert', table)
    return temp

@app.route('/stats/word/<chap>/<word>/<sid>')
def run_stats_student_word(chap, word, sid):
    r = AllReviews.getReviewDataAll()
    word = bytes(word[2: -1], 'utf8').decode('punycode')
    chap = [int(chap.split('-')[0]), int(chap.split('-')[1])]
    df = nts.getVocSource()
    df = nts.chap_filter(df, chap)
    picSrc = nts.pic_url(df, chap, word)
    df = df[df['Traditional Characters'] == word]
    eng = df['Definition (en)'].values[0]
    py = df['PinYin'].values[0]
    ex = df['Examples'].values[0].replace("_x000D_", "")
    table = main_stats.student_word(r, chap, word, sid).to_html()
    temp = render_template('word.html', 
        tradChar=word, eng=eng, PinYin=py, exSentence=ex, picSrc=picSrc)
    temp = temp.replace('Table insert', table)
    return temp

@app.route('/stats/student/<sid>/<term>')
def run_stats_student(sid, term):
    r = AllReviews.getReviewDataAll(term)
    st = g.getStudents()
    gd = g.getData()
    try: profileName = st[st['studentId']==sid]['profileName'].values[0]
    except:
        flash("抱歉, "+sid+" 學號的資料未在系統內")
        return redirect(request.referrer)
    r = r[r['student'] == profileName]

    trm = None if term=='all' else term
    df = g.st_cl_te(term=trm, studData = st, gData = gd)
    terms = list(allTerms)
    terms.remove(term)
    df = df[df['studentId'] == sid]
    df = df[['term', 'class_id', 'name', 'type', 'startUnit']]
    df['class_id'] = df['class_id'].apply(click_class)
    tablestyle = main_stats.tablestyle
    tablestyle['props'].append(('max-width', '200px'))
    table1 = df.style.format(precision=1).hide(axis='index'
            ).set_table_styles([tablestyle], overwrite=False
            ).set_table_attributes(main_stats.tabelAttr).to_html()
    table2 = main_stats.voc_analysis_html(r, click='s'+sid).set_caption('學生個人詞彙圖').to_html()
    temp = render_template('student.html', sid=sid, terms=terms, term=term)
    temp = temp.replace('Table insert1', table1).replace('Table insert2', table2)
    return temp

@app.route('/stats/class')
def run_stats_class_overview():
    message = 'Table insert'
    st = g.getStudents()
    gd = g.getData()
    df = g.st_cl_te(studData = st, gData = gd)
    df = df.groupby(['term','class_id', 'name', 'type', 'startUnit' ]).agg(學生人數=('studentId','nunique')).reset_index()
    df['class_id'] = df['class_id'].apply(click_class)
    dfr = pd.DataFrame()
    terms = []
    for i in df['term'].unique():
        dfi = df[df['term']==i].drop('term', axis=1).sort_values('學生人數', ascending=False
            ).reset_index(drop=True)
        dfi = dfi[['type', 'startUnit', 'name', '學生人數', 'class_id']]
        dfi.columns = pd.MultiIndex.from_tuples([(i, x) for x in dfi.columns.values])
        dfr = pd.concat([dfr, dfi], axis=1)
        terms.append(i)
    dfr = dfr[dfr.columns[::-1]]
    tablestyle = main_stats.tablestyle
    tablestyle['props'] += [('text-align', 'center')]
    spacing = {(n,'type'):[{'selector':'','props':[('padding-right', '25px'), ('border-right', 'solid')]}] for n in terms}
    table = dfr.style.format(precision=0, na_rep=''
            ).set_table_styles(spacing
            ).set_table_styles([main_stats.capstyle, tablestyle], overwrite=False
        ).set_table_attributes(main_stats.tabelAttr
        ).hide(axis='index').set_caption('班級總覽'
        ).to_html()
    temp = render_template('voctable.html', table=message)
    temp = temp.replace('Table insert', table)
    return temp

@app.route('/stats/class/<clss>')
def run_stats_class(clss):
    def click_st(x): return '<a href='+main_stats.statsRoot+'student/'+x+'/all>'+x+'</a>'
    st = g.getStudents()
    gd = g.getData()
    df1 = g.st_cl_te(studData = st, gData = gd)
    df = df1[df1['class_id']==clss]
    studList = df['profileName'].unique()
    df = df.groupby(['term', 'name', 'type']).agg({'studentId':'nunique'}).reset_index()
    try: trm = df['term'].values[0]
    except:
        flash("抱歉, "+clss+" 班號的資料未在系統內")
        return redirect(request.referrer)

    teacher = df['name'].values[0]
    tp = df['type'].values[0]
    nrStudents = df['studentId'].values[0]
    r = AllReviews.getReviewDataAll(trm)
    r = r[r['student'].apply(lambda x: x in studList)]
    tablestyle = main_stats.tablestyle
    tablestyle['props'] += [('max-width', '800px'), ('text-align', 'center')]
    dfc = class_stats.class_report(clss, st_cl_te=df1)[1]['df']
    dfc['學號'] = dfc['學號'].apply(click_st)
    table1 = dfc.style.hide(axis='index').hide_columns(subset=['名字', '本期複習的課']
        ).set_table_styles([tablestyle], overwrite=True
        ).set_table_attributes(main_stats.tabelAttr
        ).set_caption('').to_html()
    table2 = main_stats.voc_analysis_html(r, trm, click='c'+clss).set_caption('班級詞彙圖').to_html()
    temp = render_template('class.html', clss=clss, trm=trm, teacher=teacher, tp=tp, nrStudents=nrStudents)
    temp = temp.replace('Table insert1', table1).replace('Table insert2', table2)
    return temp

@app.route('/stats/search', methods=['GET', 'POST'])
def stats_search():
    query = request.form['name']
    # query = request.form.keys()
    print(query)
    sidRegex = re.compile("[0-9]{9}")
    classRegex = re.compile("[0-9]{5}")
    if sidRegex.match(query): 
        return redirect(main_stats.statsRoot+'student/'+query+'/all')
    elif classRegex.match(query): 
        return redirect(main_stats.statsRoot+'class/'+query)
    else: 
        flash(query+" 號碼錯誤, 請輸入學生號(9個號碼)或班號(5個號碼)")
        return redirect(request.referrer) 
        
@app.route('/all')
def run_main1():
    setting = 'all'
    thread_a = Compute(setting)
    thread_a.start()
    return 'Run all students started '+time.strftime('%H:%M:%S'), 200

@app.route('/new')
def run_main2():
    result = main.main(new=True)
    return result
    
@app.route('/sid/<id>')
def run_main3(id):
    setting = 'st'+id
    thread_a = Compute(setting)
    thread_a.start()
    return 'Student run '+id+' started '+time.strftime('%H:%M:%S'), 200

@app.route('/book/<sid>/<book>')
def run_main4(sid, book):
    setting = 'book'+sid+book
    thread_a = Compute(setting)
    thread_a.start()
    return 'Add book '+book+' sId: '+sid+' started '+time.strftime('%H:%M:%S'), 200
	
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9010)

