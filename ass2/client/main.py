from flask import render_template, Flask, redirect, url_for, jsonify, request
from config import *
import requests
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError


app = Flask(__name__)


############################ helper functions ###########################
def formatter(content, content_type='application/atom+xml'):
    # content: a bytes type
    # content_type: application/json
    # renturn: a string type
    content = content.decode('utf8')    # convert to string
    if content_type == "application/json":  # format json file
        content = content.replace('\n', '<br>')
    else: # by default xml format
        try:
            content = parseString(content)
            content = content.toprettyxml(indent='    ')
            content = content.replace('', '&nbsp')
            content = content.replace('<', '&lt')
            content = content.replace('>', '&gt')
            content = content.replace('\n', '<br>')
        except ExpatError:  # if can not format, just return
            pass
    return content


def name_to_lgaName(name):
    lgaName = name.replace(" ", "")
    if LGANAME_LOWER:
        lgaName = lgaName.lower() + 'lga'
    else:
        lgaName = lgaName.capitalize() + 'lga'
    return lgaName

############################ flask functions ############################
# home page
@app.route('/', methods=['GET'])
def index():
    return render_template("portal.html", 
        display="response content will be displayed here")


# Authentication
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    global token
    if request.method == 'GET':
        return redirect(url_for("index"))

    # get information from client
    username = request.form.get("username")
    password = request.form.get("password")

    # sent information to server
    url = URL_SERVER\
        + 'auth?username='\
        + username\
        + '&password='\
        + password

    # handle information from server
    r = requests.get(url)
    status = r.status_code
    content = r.content
    content = content.decode("utf8")
    if status == 200:   # if got token
        token = content
        content = "Congratulations! You have been authenticated as "\
                + username

    # print debug information
    if PRINT_INFO:
        print("url = ", url)
        print("username = ", username)
        print("password = ", password)
        print('status code = ', status, type(status))
        print('content = ', content, type(content))
        print('token = ', token)

    # sent information to client
    return render_template("portal.html", display=content)


# create data
@app.route('/create', methods=['GET', 'POST'])
def create():
    global token
    if request.method == 'GET':
        return redirect(url_for("index"))

    # get information from client
    lgaName = request.form.get("lgaName")
    postcode = request.form.get("postcode")
    content_type = request.form.get("contentType")

    # sent information to server
    url = URL_SERVER + 'bocsar/'
    header = {'Content-Type': content_type,
              'lgaName': lgaName,
              'postcode': postcode,
              'AUTH_TOKEN': token}

    # handle information from server
    r = requests.post(url, headers = header)
    content = formatter(r.content, content_type)

    # print debug information
    if PRINT_INFO:
        print("lgaName = ", lgaName)
        print("postcode = ", postcode)
        print("Content-Type = ", content_type)

    # sent information to client
    return render_template("portal.html", display=content)


# delete data
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    global token
    if request.method == 'GET':
        return redirect(url_for("index"))
    # get information from client
    lgaName = request.form.get("lgaName")
    lgaName = name_to_lgaName(lgaName)
    content_type = request.form.get("contentType")

    # sent information to server
    url = URL_SERVER + 'bocsar/' + lgaName
    header = {'Content-Type': content_type, 'AUTH_TOKEN': token}

    # handle information from server
    r = requests.delete(url, headers = header)
    content = formatter(r.content, content_type)

    # print debug information
    if PRINT_INFO:
        print("lgaName = ", lgaName)
        print("Content-Type = ", content_type)

    # sent information to client
    return render_template("portal.html", display=content)


# read single data
@app.route('/read', methods=['GET', 'POST'])
def read():
    global token
    if request.method == 'GET':
        return redirect(url_for("index"))
    # get information from client
    lgaName = request.form.get("lgaName")
    lgaName = name_to_lgaName(lgaName)
    content_type = request.form.get("contentType")

    # sent information to server
    url = URL_SERVER + 'bocsar/' + lgaName
    header = {'Content-Type': content_type, 'AUTH_TOKEN': token}

    # handle information from server
    r = requests.get(url, headers = header)
    content = formatter(r.content, content_type)

    # print debug information
    if PRINT_INFO:
        print("lgaName = ", lgaName)
        print("Content-Type = ", content_type)

    # sent information to client
    return render_template("portal.html", display=content)


# list all data
@app.route('/list', methods=['GET', 'POST'])
def list_all():
    global token
    if request.method == 'GET':
        return redirect(url_for("index"))
    # get information from client
    content_type = request.form.get("contentType")

    # sent information to server
    url = URL_SERVER + 'bocsar/'
    header = {'Content-Type': content_type, "AUTH_TOKEN": token}

    # handle information from server
    r = requests.get(url, headers = header)
    content = formatter(r.content, content_type)

    # print debug information
    if PRINT_INFO:
        print("Content-Type = ", content_type)

    # sent information to client
    return render_template("portal.html", display=content)


# query data
@app.route('/query', methods=['GET', 'POST'])
def query():
    global token
    if request.method == 'GET':
        return redirect(url_for("index"))

    # get information from client
    query = request.form.get("query")
    content_type = request.form.get("contentType")

    # sent information to server
    url = URL_SERVER + 'bocsar/filter?' + query
    header = {'Content-Type': content_type, 'AUTH_TOKEN': token}

    # handle information from server
    r = requests.get(url, headers = header)
    content = formatter(r.content, content_type)

    # print debug information
    if PRINT_INFO:
        print("query = ", query)
        print("Content-Type = ", content_type)

    # sent information to client
    return render_template("portal.html", display=content)


if __name__ == "__main__":
    token = ""
    app.run(port=5001)