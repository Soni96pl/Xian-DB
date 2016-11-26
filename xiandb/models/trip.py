from datetime import date, datetime

from ..field import Field, Protected, Id, Reference
from ..document import Document
from ..collection import Collection


class TripDocument(Document):
    structure = {
        '_id': Id(),
        '_user': Protected(int),
        'name': Field(basestring, required=True),
        'date': Field(date, required=True),
        'transport': [{
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
        }],
        'lodging': [{
            'city': Reference('cities', required=True),
            'check_in': Field(datetime),
            'check_out': Field(datetime),
            'property': {
              'name': Field(unicode),
              'type': Field(unicode),
              'location': {
                  'address': Field(unicode),
                  'coordinates': [Field(float)],
                  'instructions': Field(unicode)
              },
              'contact': {
                  'phone': Field(int),
                  'email': Field(unicode)
              }
            },
            'room': {
                'name': Field(unicode),
                'type': Field(unicode)
            },
            'balance': {
                'deposit': {
                    'value': Field(float),
                    'currency': Field(unicode)
                },
                'remaining': {
                    'value': Field(float),
                    'currency': Field(unicode)
                }
            },
            'conditions': Field(unicode)
        }]
    }


class TripCollection(Collection):
    __collection__ = 'trips'
    document_class = TripDocument
