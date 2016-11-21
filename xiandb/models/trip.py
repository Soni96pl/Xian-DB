from datetime import date, datetime

from ..field import Id, Reference, Field
from ..document import Document
from ..collection import Collection


class TripDocument(Document):
    structure = {
        '_id': Id(),
        'user_id': Field(int, required=True),
        'name': Field(basestring, required=True),
        'date': Field(date, required=True),
        'transport': [{
            '_id': Id(counter_name='transportid'),
            'carrier': Reference('carriers'),
            'code': Field(basestring),
            'mode': Field(basestring),
            'departure': {
                'station': Reference('stations'),
                'time': Field(datetime)
            },
            'arrival': {
                'station': Reference('stations'),
                'time': Field(datetime),
            },
            'price': {
                'value': Field(float),
                'currency': Field(basestring)
            },
            'booking': {
                'ref': Field(basestring),
                'url': Field(basestring)
            },
            'conditions': Field(basestring)
        }]
    }


class TripCollection(Collection):
    __collection__ = 'trips'
    document_class = TripDocument
