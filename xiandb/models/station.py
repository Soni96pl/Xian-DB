from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection


class StationDocument(Document):
    structure = {
        '_id': int,
        'name': unicode,
        'code': unicode,
        'type': unicode,
        'city_id': int,
        'location': {
            'address': unicode,
            'coordinates': [float],
            'instructions': unicode
        },
        'contact': {
            'phone': unicode,
            'email': unicode
        },
        'status': unicode,
        'contributor': int,
        'transfer': [int]
    }
    unique = ['name']

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)


class StationCollection(Collection):
    __collection__ = 'stations'
    __database__ = config.mongodb['database']
    document_class = StationDocument
