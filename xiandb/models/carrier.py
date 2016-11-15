from datetime import date, datetime

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection


class CarrierDocument(Document):
    structure = {
        'name': unicode,
        'type': unicode,
        'contact': {
            'phone': unicode,
            'email': unicode
        },
        'stations': [int]
    }
    unique = ['name']

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)


class CarrierCollection(Collection):
    __collection__ = 'carriers'
    __database__ = config.mongodb['database']
    document_class = CarrierDocument
