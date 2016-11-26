from ..field import Field, Protected, Id, Reference
from ..document import Document
from ..collection import Collection


class StationDocument(Document):
    structure = {
        '_id': Id(),
        '_user': Protected(int),
        'name': Field(basestring, required=True),
        'code': Field(basestring),
        'type': Field(basestring, required=True),
        'city': Reference('cities', required=True),
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
        'transfer': [Field(int)]
    }


class StationCollection(Collection):
    __collection__ = 'stations'
    document_class = StationDocument
