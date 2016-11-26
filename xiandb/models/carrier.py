from ..field import Field, Protected, Id
from ..document import Document
from ..collection import Collection


class CarrierDocument(Document):
    structure = {
        '_id': Id(),
        '_user': Protected(int),
        'name': Field(basestring, required=True),
        'type': Field(basestring),
        'contact': {
            'phone': Field(basestring),
            'email': Field(basestring)
        },
        'status': Field(basestring)
    }


class CarrierCollection(Collection):
    __collection__ = 'carriers'
    document_class = CarrierDocument
