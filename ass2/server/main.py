import xlrd
import urllib
import simplejson
import models
import xmltodict
from flask import jsonify
from collections import defaultdict


URL_BOCSAR = "http://resource.mcndsj.com/lga/"
URL_AUPOST = """https://docs.google.com/spreadsheets/d/1tHCxouhyM4edDvF6\
                0VG7nzs5QxID3ADwr3DGJh71qFg/edit#gid=900781287"""
PATH_XLSX = "./xlsx/"
JSON_PATH = "./json/"


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

############################# main function #############################
postcode_to_region = read_postcode()

# name = "Balranaldlga"
# # download_xlsx(name)
# my_dict = read_excel(name)
# my_json = simplejson.dumps(my_dict)
# # print(xmltodict.unparse(my_json))
# # wirte_json(name, my_json)
# # models.save_database(name, my_json)
# print(models.query_database(name))