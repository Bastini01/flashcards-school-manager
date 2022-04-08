from flask import Flask, url_for ,render_template
# from SRL.scripts import main, listener
import main
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
    # listener.act(id)
    result = main.main(idFilter=id)
    # return "The URL for this page is {}".format(url_for('bar'))
    return result

# def foo_with_slug(adapter, id):
#     # ask the database for the slug for the old id.  this of
#     # course has nothing to do with werkzeug.
#     return f'foo/{Foo.get_slug_for_id(id)}'

# app.add_url_rule('/<id>', view_func=run_main)
	
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9010)