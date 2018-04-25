import xlrd
import urllib
import simplejson
import models
import xmltodict
import dicttoxml
from functools import wraps
from collections import defaultdict
from flask import jsonify, request, Flask
from flask_restful import reqparse, request, abort
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)


URL_BOCSAR = "http://resource.mcndsj.com/lga/"
URL_AUPOST = """https://docs.google.com/spreadsheets/d/1tHCxouhyM4edDvF6\
                0VG7nzs5QxID3ADwr3DGJh71qFg/edit#gid=900781287"""
PATH_XLSX = "./xlsx/"
JSON_PATH = "./json/"
SECRET_KEY = "A RANDOM KEY"


############################ helper function ############################
def download_xlsx(name):
    try:
        urllib.request.urlretrieve(URL_BOCSAR + name + '.xlsx', \
                PATH_XLSX + name + '.xlsx')
    except urllib.error.HTTPError:
        print("Could not download!")


def read_excel(name):
    # open the first sheet
    wb = xlrd.open_workbook(PATH_XLSX + name + '.xlsx')
    sh = wb.sheet_by_index(0)

    # generate titles
    year = sh.row_values(5)[2:]
    category = sh.row_values(6)[2:]
    title = category[:]
    ntitle = len(title)
    for i in range(ntitle):
        if (category[i] == 'Number of incidents'\
                or category[i] == 'Rate per 100,000 population'):
            title[i] = year[int(i/2) * 2] + ' ' +  title[i]

    # generate dictionary
    my_dict = {}
    for i in range(7, sh.nrows - 14):
        # create new group
        if sh.row_values(i)[0] != '':
            group_key = sh.row_values(i)[0]
            group_value = {}
        # create new type
        type_key =  sh.row_values(i)[1]
        type_value = {}
        # add key and value to type
        for j in range(ntitle):
            type_value[title[j]] = sh.row_values(i)[j + 2]
        # add type to group
        group_value[type_key] = type_value
        # add group to dictionary
        my_dict[group_key] = group_value

    # function return
    return my_dict


def wirte_json(name, my_json):
    # write to json file
    with open(JSON_PATH + name + '.json', 'w') as json:
        json.write(my_json)


def read_postcode():
    # open postcode
    wb = xlrd.open_workbook(PATH_XLSX + 'postcode' + '.xlsx')
    sh = wb.sheet_by_index(0)
    # generate list
    nlines = 1780
    region = sh.col_values(1)[1:nlines + 1]
    postcode = sh.col_values(2)[1:nlines + 1]
    # create dictionary
    postcode_to_region = defaultdict(list)
    for i in range(nlines):
        postcode_to_region[int(postcode[i])].append(region[i])
    # function return
    return postcode_to_region

 
######################## authentication function ########################

def authenticate_by_token(token, must_admin=False):
    if token is None:
        return False
    s = Serializer(SECRET_KEY)
    try:
        username = s.loads(token.encode())
        if must_admin:  # only allow admin to login
            if username == 'admin':
                return True
        else:   # allow everyone to login
            if ((username == 'admin') or (username == 'guest')):
                return True
    except:
        return False

    return False


# login as admin or guest
def login_required(f, message="You are not authorized"):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get("AUTH_TOKEN")
        print("token=", token)
        if authenticate_by_token(token, must_admin=False):
            return f(*args, **kwargs)

        return jsonify(message=message), 401
        # abort(401, message=message)

    return decorated_function


# only allowed login as admin
def admin_login_required(f, message="You are not authorized"):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get("AUTH_TOKEN")
        if authenticate_by_token(token, must_admin=True):
            return f(*args, **kwargs)

        return jsonify(message=message), 401
        # abort(401, message=message)

    return decorated_function


############################# REST function #############################
app = Flask(__name__)


@app.route("/admin", methods=['GET'])
@admin_login_required
def test():
    print("You are admin!")


@app.route("/", methods=['GET'])
@login_required
def gogogo():
    print("You are login!")


@app.route("/auth", methods=['GET'])
def generate_token():
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        args = parser.parse_args()

        username = args.get("username")
        password = args.get("password")

        # debug function
        # print("Username =", username)
        # print("Password =", password)

        s = Serializer(SECRET_KEY, expires_in=600)
        token = s.dumps(username)

        if ((username == 'admin' and password == 'admin')
                or (username == 'guest' and password == 'guest')):
            return token.decode()

        return jsonify({"ERROR" : "wrong username or password"}), 404


############################# main function #############################
if __name__ == "__main__":
    app.run()
    # postcode_to_region = read_postcode()
    # name = "Balranaldlga"
    # # # download_xlsx(name)
    # my_dict = read_excel(name)
    # # my_json = simplejson.dumps(my_dict)
    # my_xml = dicttoxml.dicttoxml(
    #         my_dict, 
    #         attr_type=False, 
    #         root=False)

    # print(str(my_xml))
    # print(my_dict)
    # # print(xmltodict.unparse(my_json))
    # # wirte_json(name, my_json)
    # # models.save_database(name, my_json)
    # print(models.query_database(name))