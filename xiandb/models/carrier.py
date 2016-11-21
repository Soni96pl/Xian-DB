from ..field import Field, Id
from ..document import Document
from ..collection import Collection


class CarrierDocument(Document):
    structure = {
        '_id': Id(),
        'name': Field(basestring, required=True),
        'type': Field(basestring),
        'contact': {
            'phone': Field(basestring),
            'email': Field(basestring)
        },
        'status': Field(basestring),
        'contributor': Field(int)
    }

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)


class CarrierCollection(Collection):
    __collection__ = 'carriers'
    document_class = CarrierDocument
