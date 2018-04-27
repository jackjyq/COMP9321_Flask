import xlrd
import urllib
import simplejson
import models
import xmltodict
import dicttoxml
import json
import re
from copy import deepcopy
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


# def read_excel_by_group(name):
#     # open the first sheet
#     wb = xlrd.open_workbook(XLSX_PATH + name + '.xlsx')
#     sh = wb.sheet_by_index(0)

#     # generate titles
#     year = sh.row_values(5)[2:]
#     category = sh.row_values(6)[2:]
#     title = category[:]
#     ntitle = len(title)
#     for i in range(ntitle):
#         if (category[i] == 'Number of incidents'\
#                 or category[i] == 'Rate per 100,000 population'):
#             title[i] = year[int(i/2) * 2] + ' ' +  title[i]

#     # generate dictionary
#     my_dict = {}
#     for i in range(7, sh.nrows - 14):
#         # create new group
#         if sh.row_values(i)[0] != '':
#             group_key = sh.row_values(i)[0]
#             group_value = {}
#         # create new type
#         type_key =  sh.row_values(i)[1]
#         type_value = {}
#         # add key and value to type
#         for j in range(ntitle):
#             type_value[title[j]] = sh.row_values(i)[j + 2]
#         # add type to group
#         group_value[type_key] = type_value
#         # add group to dictionary
#         my_dict[group_key] = group_value

#     # function return
#     return my_dict


def read_excel_by_year(name):
    # open the first sheet
    wb = xlrd.open_workbook(XLSX_PATH + name + '.xlsx')
    sh = wb.sheet_by_index(0)



    # generate years
    years = re.findall(r'\d+', ''.join(sh.row_values(5)[2:]))
    nyears = len(years)

    if PRINT_INFO:
        print("years = ", years)
        print("number of years = ", nyears)

    # initialize dictionary, return None if empty
    my_dict = defaultdict(lambda: None)
    for i in range(nyears + 1): # the extra 1 is for trend
        if i < nyears: # for year
            year_key = years[i]
        else:   # for trend
            year_key = "trend"
        year_value = {}
        # iterate rows of excel
        for row in range(7, sh.nrows - 14):
            # create group
            if sh.row_values(row)[0] != '':
                group_key = sh.row_values(row)[0]
                group_value = {}
            # create type
            type_key =  sh.row_values(row)[1]
            type_value = {}
            # add item to type
            if i < nyears: # for year
                type_value["number"] = sh.row_values(row)[2 + i*2]
                type_value["rate"] = sh.row_values(row)[2 + i*2 + 1]
            else:   # for trend
                type_value["24_mon_trend"] = sh.row_values(row)[2 + i*2]
                type_value["60_mon_trend"] = sh.row_values(row)[2 + i*2 + 1]
                type_value["rank"] = sh.row_values(row)[2 + i*2 + 2]
            # add type to group
            group_value[type_key] = type_value
            # add group to year
            year_value[group_key] = group_value
            # add year to dictionary
            my_dict[year_key] = year_value
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
        lgaName = name_to_lgaName(region[i])
        postcode_to_region[int(postcode[i])].append(lgaName)
    # function return
    return postcode_to_region


def name_to_lgaName(name):
    lgaName = name.replace(" ", "")
    if LGANAME_LOWER:
        lgaName = lgaName.lower() + 'lga'
    else:
        lgaName = lgaName.capitalize() + 'lga'
    return lgaName
 
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
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get("AUTH_TOKEN")
        print("token=", token)
        if authenticate_by_token(token, must_admin=False):
            return f(*args, **kwargs)

        return "Error: You are not authorized", 401

    return decorated_function


# only allowed login as admin
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get("AUTH_TOKEN")
        if authenticate_by_token(token, must_admin=True):
            return f(*args, **kwargs)

        return "Error: You are not authorized", 401

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
        lgaName = name_to_lgaName(lgaName)
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
                    my_dict = read_excel_by_year(name)
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
        my_dict["Error: "] = id + " not found!"
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
        my_dict["OK: "] = id + " has been deleted!"
        status_code = 200
    except KeyError:
        my_dict["Error: "] = id + " not found!"
        status_code = 404
    
    if PRINT_INFO:
        print("my_dict = ", my_dict)
		
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
    # get header
    content_type = request.headers.get("Content-Type")

    # parse query string
    query_list = request.query_string.decode("utf-8").split("%20")
    query_filter = defaultdict(set)
    if ((len(query_list) + 1) % 4 == 0):    # valid number of operand
        group_of_operand = int((len(query_list) + 1) / 4)
        for i in range(group_of_operand):
            query_filter[query_list[4*i]].add(query_list[4*i + 2])

    if PRINT_INFO:
        print("Content-Type = ", content_type)
        print("query string = ", query_list)
        print("lgaName = ", query_filter['lgaName'])
        print("year = ", query_filter['year'])

    # generate return dict and status_code
    return_dict = {}
    status_code = 200
    for name in query_filter['lgaName']:
        name = name_to_lgaName(name)
        if name in lgaName_database:
        # for every name exist in database and filter
            name_dict = {}
            # retreive json from database and convert to dict
            my_json = models.query_database(name)
            my_dict = json.loads(my_json)

            if query_filter['year']:
            # apply year filter if exist
                for year in query_filter['year']:
                    if year in my_dict.keys():
                    # for every year exist in database and filter
                        name_dict[year] = my_dict[year]
            else:   # if year filter not exist
                name_dict = my_dict
            # add name_dict to return_dict
            return_dict[name] = deepcopy(name_dict)

    # return json
    if content_type == "application/json":
        return jsonify(return_dict), 200
    else:   # return xml(by default)
        return  dicttoxml.dicttoxml(
                return_dict, 
                attr_type=False, 
                custom_root="entry"), 200

# authentication
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
            return token.decode(), 200

        return "ERROR: wrong username or password", 401


############################# main function #############################
if __name__ == "__main__":
    postcode_database = read_postcode()
    lgaName_database = set()
    if INITIAL_SETUP:
        lgaName_database = set(['Boganlga', 'Lachlanlga', 'Cobarlga', 'Blandlga', 'Carrathoollga', 'Forbeslga'])
    app.run()

