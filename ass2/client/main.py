from flask import render_template, Flask, redirect, url_for, jsonify, request
from config import *
import requests
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("portal.html", display="OK")


@app.route('/list', methods=['POST'])
def list_all():
    lgaName = request.form.get("lgaName")
    postcode = request.form.get("postcode")
    content_type = request.form.get("contentType")

    url = URL_SERVER + 'bocsar/'
    header = {'Content-Type': 'application/json'}
    r = requests.get(url, headers = header)
    content = r.content
    content = content.decode('utf8')
    content = content.replace('\n', '<br>')

    if PRINT_INFO:
        print("content ", type(content), " = \n", content)
        print("lgaName = ", lgaName)
        print("postcode", postcode)
        print("Content-Type = ", content_type)

    return render_template("portal.html", display=content)

if __name__ == "__main__":
   app.run(debug=True, port=5001)