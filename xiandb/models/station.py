from xiandb import config
from xiandb.field import Id, Field, Reference
from xiandb.document import Document
from xiandb.collection import Collection
from xiandb.models import city


class StationDocument(Document):
    structure = {
        '_id': Id(),
        'name': Field(unicode, required=True, unique=True),
        'code': Field(unicode),
        'type': Field(unicode, required=True),
        'city': Reference(city.CityCollection),
        'location': {
            'address': Field(unicode),
            'coordinates': [Field(float)],
            'instructions': Field(unicode)
        },
        'contact': {
            'phone': Field(unicode),
            'email': Field(unicode)
        },
        'status': Field(unicode),
        'contributor': Field(int),
        'transfer': [Field(int)]
    }

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)


class StationCollection(Collection):
    __collection__ = 'stations'
    __database__ = config.mongodb['database']
    document_class = StationDocument
