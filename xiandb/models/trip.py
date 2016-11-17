from datetime import date, datetime

from xiandb import config
from xiandb.field import Id, Reference, Field
from xiandb.document import Document
from xiandb.collection import Collection
from xiandb.models import carrier, station


class TripDocument(Document):
    structure = {
        '_id': Id(),
        'user_id': Field(int, required=True),
        'name': Field(unicode, required=True),
        'date': Field(date, required=True),
        'transport': [{
            '_id': Id(counter='transportid'),
            'carrier': Reference(carrier.CarrierCollection),
            'code': Field(unicode),
            'mode': Field(unicode),
            'departure': {
                'station': Reference(station.StationCollection),
                'time': Field(datetime)
            },
            'arrival': {
                'station': Reference(station.StationCollection),
                'time': Field(datetime),
            },
            'price': {
                'value': Field(float),
                'currency': Field(unicode)
            },
            'booking': {
                'ref': Field(unicode),
                'url': Field(unicode)
            },
            'conditions': Field(unicode)
        }]
    }
    unique = ['name']

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.validators['transport'] = [
            lambda f: f['departure'] < f['arrival'],
            lambda f: not any(map(
                lambda e: any([
                    '_id' in f and f['_id'] != e['_id'],
                    not all([
                        f['departure'] < e['arrival'],
                        f['arrival'] > e['departure']
                    ])
                ]),
                self['transport']
            ))
        ]


class TripCollection(Collection):
    __collection__ = 'trips'
    __database__ = config.mongodb['database']
    document_class = TripDocument
