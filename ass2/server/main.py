import requests
import openpyxl     # http://zetcode.com/articles/openpyxl/
import urllib

BOCSAR = "http://resource.mcndsj.com/lga/"
AUPOST = """https://docs.google.com/spreadsheets/d/1tHCxouhyM4edDvF60VG7\
            nzs5QxID3ADwr3DGJh71qFg/edit#gid=900781287"""
XLSXPATH = "./xlsx/"

xlsx_name = "Balranaldlga.xlsx"
xlsx_url = BOCSAR + xlsx_name
print("xlsx_url = ", xlsx_url)

# download the excel file
# try:
#     urllib.request.urlretrieve(xlsx_url, XLSXPATH + xlsx_name)
# except urllib.error.HTTPError:
#     print("Could not download!")

xlsx_workbook = openpyxl.load_workbook(filename = XLSXPATH + xlsx_name,\
                                        read_only=True)
                                        
sheet_name = xlsx_workbook.sheetnames[0]
xlsx_sheet = xlsx_workbook[sheet_name]

for row in xlsx_sheet.rows:
    print("\n")
    for cell in row:
        print(cell.value)