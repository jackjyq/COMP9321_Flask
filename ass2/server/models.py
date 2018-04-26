from mongoengine import connect,StringField, Document
from config import DB_CONNECT


class database(Document):
    y2010 = StringField(required = True)
    name = StringField(required = True)
    def __init__(self, name, data, *args, **values):
        super().__init__(*args, **values)
        self.name = name
        self.data = data


def save_database(name ,my_json):
    connect(host=DB_CONNECT)
    data = database(name ,my_json)
    data.save()

# return a string or None
def query_database(lgaName):
    connect(host=DB_CONNECT)
    record = database.objects(name = lgaName)
    for t in record:
        return t.data