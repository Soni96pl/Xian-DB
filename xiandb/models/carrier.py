from xiandb import config
from xiandb.field import Field, Id
from xiandb.document import Document
from xiandb.collection import Collection


class CarrierDocument(Document):
    structure = {
        '_id': Id(),
        'name': Field(unicode, required=True),
        'type': Field(unicode),
        'contact': {
            'phone': Field(unicode),
            'email': Field(unicode)
        },
        'status': Field(unicode),
        'contributor': Field(int)
    }

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)


class CarrierCollection(Collection):
    __collection__ = 'carriers'
    __database__ = config.mongodb['database']
    document_class = CarrierDocument
