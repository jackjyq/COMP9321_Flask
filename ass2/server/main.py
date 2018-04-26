import xlrd
import urllib
import simplejson
import models
import xmltodict
import dicttoxml
import json
from functools import wraps
from collections import defaultdict
from datetime import datetime, timezone       
from flask import jsonify, request, Flask
from flask_restful import reqparse, request, abort
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
from config import *


############################ helper function ############################
def download_xlsx(name):
# if can be downloaded ,return true
# if can not be found, return false
    try:
        url = URL_BOCSAR + name + '.xlsx'
        urllib.request.urlretrieve(url, XLSX_PATH + name + '.xlsx')
    except urllib.error.HTTPError:
        if PRINT_INFO:
            print("Could not download from ", url)
        return False
        if PRINT_INFO:
            print("Finish downloading ", url)
    return True


def read_excel(name):
    # open the first sheet
    wb = xlrd.open_workbook(XLSX_PATH + name + '.xlsx')
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
    wb = xlrd.open_workbook(XLSX_PATH + 'postcode' + '.xlsx')
    sh = wb.sheet_by_index(0)
    # generate list
    nlines = 1780
    region = sh.col_values(1)[1:nlines + 1]
    postcode = sh.col_values(2)[1:nlines + 1]
    # create dictionary
    postcode_to_region = defaultdict(list)
    for i in range(nlines):
        # normilize lgaName
        lgaName = region[i].replace(" ", "")
        if LGANAME_LOWER:
            lgaName = lgaName.lower() + 'lga'
        else:
            lgaName = lgaName.capitalize() + 'lga'
        postcode_to_region[int(postcode[i])].append(lgaName)
    # function return
    return postcode_to_region

 
######################## authentication function ########################

def authenticate_by_token(token, must_admin=False):
    if not LOGIN_NEED:
        return True
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


# create
@app.route("/bocsar/", methods=['POST'])
@admin_login_required
def create():
    # get the HTTP arguments
    lgaName = request.headers.get("lgaName")
    postcode = request.headers.get("postcode")
    content_type = request.headers.get("Content-Type")
    # a list that store lgaName, may be more than 1 name
    lgaName_list = []
    if postcode:
        lgaName_list = postcode_database[int(postcode)][:]
    # normilize lgaName
    if lgaName:
        lgaName = lgaName.replace(" ", "")
        if LGANAME_LOWER:
            lgaName = lgaName.lower() + 'lga'
        else:
            lgaName = lgaName.capitalize() + 'lga'
        lgaName_list.append(lgaName)
    
    # save to database
    lgaName_to_return = set()
    for name in lgaName_list:
        # check whether it is in lgaName_database
        if name in lgaName_database:
            lgaName_to_return.add(name)
        else:
        # check whether it is in database by query
            my_jason = models.query_database(name)
            if my_jason:
                lgaName_to_return.add(name)
                lgaName_database.add(name)
            else:
            # try to download the excel and add it to database
                if download_xlsx(name):
                    my_dict = read_excel(name)
                    my_json = simplejson.dumps(my_dict)
                    models.save_database(name, my_json)
                    lgaName_to_return.add(name)
                    lgaName_database.add(name)

    # check the database
    if PRINT_INFO:
        print("lgaName = ", lgaName)
        print("postcode = ", postcode)
        print("Content-Type = ", content_type)
        print("lgaName_list = ", lgaName_list)
        print("lgaName_for_return = ", lgaName_to_return)
        print("lgaName_database = ", lgaName_database)

    # generate return dictionary
    my_dict = {}
    for name in lgaName_to_return:
        my_dict[name] = {
            "title": name,
            "url": URL_COLLECTION + name
        }

    # generate reture code and error message
    if my_dict:
        status_code = 201
    else:
        my_dict["ERROR"] = "Nothing created!"
        status_code = 400

    # return json
    if content_type == "application/json":
        return jsonify(my_dict), status_code
    else:   # return xml(by default)
        return  dicttoxml.dicttoxml(
                my_dict, 
                attr_type=False, 
                custom_root="entry"), status_code


# read
@app.route("/bocsar/<id>", methods=['GET'])
@login_required
def read(id):
    content_type = request.headers.get("Content-Type")
    # check the database
    if PRINT_INFO:
        print("Content-Type = ", content_type)

    my_dict = {}
    if id in lgaName_database:
        my_json = models.query_database(id)
        my_dict = json.loads(my_json)
        status_code = 200
    else:
        my_dict["Error: "] = {id + " not found!"}
        status_code = 404

    # return json
    if content_type == "application/json":
        return jsonify(my_dict), status_code
    else:   # return xml(by default)
        return  dicttoxml.dicttoxml(
                my_dict, 
                attr_type=False, 
                custom_root="entry"), status_code


# delete
@app.route("/bocsar/<id>", methods=['DELETE'])
@admin_login_required
def delete(id):
    content_type = request.headers.get("Content-Type")
    # check the database
    if PRINT_INFO:
        print("Content-Type = ", content_type)

    my_dict = {}
    try:
        lgaName_database.remove(id)
        my_dict["OK: "] = {id + " has been deleted!"}
        status_code = 200
    except KeyError:
        my_dict["Error: "] = {id + " not found!"}
        status_code = 404

    # return json
    if content_type == "application/json":
        return jsonify(my_dict), status_code
    else:   # return xml(by default)
        return  dicttoxml.dicttoxml(
                my_dict, 
                attr_type=False, 
                custom_root="entry"), status_code


# retrieve list
@app.route("/bocsar/", methods=['GET'])
@login_required
def retrieve():
    content_type = request.headers.get("Content-Type")
    # check the database
    if PRINT_INFO:
        print("Content-Type = ", content_type)

    # generate return dictionary
    my_dict = {}
    for name in lgaName_database:
        my_dict[name] = {
            "title": name,
            "url": URL_COLLECTION + name
        }

    # return json
    if content_type == "application/json":
        return jsonify(my_dict), 200
    else:   # return xml(by default)
        return  dicttoxml.dicttoxml(
                my_dict, 
                attr_type=False, 
                custom_root="entry"), 200


# query
@app.route("/bocsar/filter", methods=['GET'])
@login_required
def query():
    # get header and query string
    content_type = request.headers.get("Content-Type")
    query_list = request.query_string.decode("utf-8").split("%20")

    # check the database
    if PRINT_INFO:
        print("Content-Type = ", content_type)
        print("query string = ", query_list)

    
    
    return "hello"


@app.route("/auth", methods=['GET'])
def generate_token():
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        args = parser.parse_args()

        username = args.get("username")
        password = args.get("password")

        if PRINT_INFO:
            print("Username =", username)
            print("Password =", password)

        s = Serializer(SECRET_KEY, expires_in=600)
        token = s.dumps(username)

        if ((username == 'admin' and password == 'admin')
                or (username == 'guest' and password == 'guest')):
            return token.decode()

        return jsonify({"ERROR" : "wrong username or password"}), 404


############################# main function #############################
if __name__ == "__main__":
    postcode_database = read_postcode()
    lgaName_database = set(['Boganlga', 'Lachlanlga', 'Cobarlga', 'Blandlga', 'Carrathoollga', 'Forbeslga'])
    app.run()


    # d = datetime.utcnow() # <-- get time in UTC
    # print(d.isoformat("T") + "Z")

    # name = "Boganlga"
    # # # # 
    # 
    # my_json = simplejson.dumps(my_dict)
    # # my_xml = dicttoxml.dicttoxml(
    # #         my_dict, 
    # #         attr_type=False, 
    # #         root=False)

    # # print(str(my_xml))
    # print(my_dict)
    # # # wirte_json(name, my_json)
    # models.save_database(name, my_json)
    # my_dict = json.loads(models.query_database(name))
    # print(type(my_dict))
    # print(my_dict)
    # if (models.query_database(name)):
    #     print('yes')
    # else:
    #     print('no')
    # models.getkey_database()
    # print(lgaName_database)

