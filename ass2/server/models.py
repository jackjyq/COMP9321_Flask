from mongoengine import connect,StringField, Document

class database(Document):
    data = StringField(required = True)
    name = StringField(required = True)
    def __init__(self, name, data, *args, **values):
        super().__init__(*args, **values)
        self.name = name
        self.data = data


def save_database(name ,my_json):
    connect(host='mongodb://jack_jiang:comp9321@ds247759.mlab.com:47759/my-database')
    data = database(name ,my_json)
    data.save()


def query_database(lgaName):
    connect(host='mongodb://jack_jiang:comp9321@ds247759.mlab.com:47759/my-database')
    record = database.objects(name = lgaName)
    for t in record:
        return t.data