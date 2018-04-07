from flask import Flask
from flask import request
from flask import make_response, redirect, abort
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    this = request.headers.get('User-Agent')
    response = make_response("{0}{1}".format("Your browser is ",this))
    return response

@app.route('/<site>')
def site(site):
    return redirect("{}{}{}".format("http://www.", site, ".com"))
if __name__ == '__main__':
    manager.run()
