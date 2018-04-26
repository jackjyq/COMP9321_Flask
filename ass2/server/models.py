from mongoengine import connect,StringField, Document
from config import DB_CONNECT


class Database(Document):
    name = StringField(required=True, primary_key=True)
    data = StringField(required=True)

    def __init__(self, name, data, *args, **values):
        super().__init__(*args, **values)
        self.name = name
        self.data = data


def save_database(name, my_json):
    connect(host=DB_CONNECT)
    instance = Database(name, my_json)
    instance.save()


# return a string or None
def query_database(lgaName):
    connect(host=DB_CONNECT)
    for t in Database.objects(name=lgaName):
        # print(t.data)
        return t.data