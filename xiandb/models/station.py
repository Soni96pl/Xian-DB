from ..field import Id, Field, Reference
from ..document import Document
from ..collection import Collection


class StationDocument(Document):
    structure = {
        '_id': Id(),
        'name': Field(basestring, required=True, unique=True),
        'code': Field(basestring),
        'type': Field(basestring, required=True),
        'city': Reference('cities'),
        'location': {
            'address': Field(basestring),
            'coordinates': [Field(float)],
            'instructions': Field(basestring)
        },
        'contact': {
            'phone': Field(basestring),
            'email': Field(basestring)
        },
        'status': Field(basestring),
        'contributor': Field(int),
        'transfer': [Field(int)]
    }


class StationCollection(Collection):
    __collection__ = 'stations'
    document_class = StationDocument
