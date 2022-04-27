import time
import datetime as dt
import sys
from os.path import join
from flask import Flask, request, url_for ,render_template
from threading import Thread
import main, main_stats
app = Flask(__name__)
app.debug = True

original_stdout = sys.stdout
logFilePath=join(main_stats.logPath,"flasktest"+dt.datetime.now().strftime('%y%m%d%H%M')+".txt")
logFile = open(join(logFilePath),'w', encoding="utf-8")
today=dt.datetime.now().date()


def switchPrint():
    sys.stdout = logFile

def closelog():
    logFile.close()
    sys.stdout = original_stdout

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
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        # time.sleep(120)
        main.main(idFilter = self.id)
        # switchPrint()
        # print("start")
        # time.sleep(60)
        # print(self.request)
        # print('Student run started '+time.strftime('%H:%M:%S'))
        # print("done")
        # closelog()

def testfunc(id):
    print('hello')

@app.route('/all')
def run_main1():
    result = main.main(std=True)
    return result

@app.route('/new')
def run_main2():
    result = main.main(new=True)
    return result

@app.route('/sid/<id>')
def run_main3(id):
    thread_a = Compute(id)
    thread_a.start()
    return 'Student run '+id+' started '+time.strftime('%H:%M:%S'), 200
	
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9010)

