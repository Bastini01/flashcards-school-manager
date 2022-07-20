from posixpath import split
import time, re
from flask import Flask, render_template
from threading import Thread
import main, main_stats, AllReviews
import config_notes as nts

app = Flask(__name__)
app.debug = True

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



@app.route('/stats/voc/<term>')
def run_stats_voc(term):
    r = AllReviews.getReviewDataAll(term)
    message = 'Table insert'
    terms = ['21winter', '22spring', '22summer', 'all']
    terms.remove(term)
    table = main_stats.voc_analysis_html(r, click=True).to_html()
    temp = render_template('voctable.html', table=message, terms=terms, term=term)
    temp = temp.replace('Table insert', table)
    return temp

@app.route('/stats/word/<chap>/<word>')
def run_stats_word(chap, word):
    r = AllReviews.getReviewDataAll()
    word = bytes(word[2: -1], 'utf8').decode('punycode')
    chap = [int(chap.split('-')[0]), int(chap.split('-')[1])]
    df = nts.getVocSource()
    df = df[df['TextbookChapter'].apply(lambda x:x.split("-")[0]) == nts.vuName(
            [chap[0], chap[1], 1]).split('-')[0]]
    df = df[df['Traditional Characters'] == word]
    eng = df['Definition (en)'].values[0]
    py = df['PinYin'].values[0]
    ex = df['Examples'].values[0]
    table = main_stats.word_student(r, chap, word).to_html()
    temp = render_template('word.html', 
        tradChar=word, eng=eng, PinYin=py, exSentence=ex)
    temp = temp.replace('Table insert', table)
    return temp

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

