from datetime import date, datetime

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection


class StationDocument(Document):
    structure = {
        'name': unicode,
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
        'transfer': [int],
        'carriers': [int]
    }
    unique = ['name']

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)


class StationCollection(Collection):
    __collection__ = 'stations'
    __database__ = config.mongodb['database']
    document_class = StationDocument
