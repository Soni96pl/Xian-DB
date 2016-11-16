from datetime import date, datetime

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection
from xiandb.models import carrier, station


class TripDocument(Document):
    structure = {
        '_id': int,
        'user_id': int,
        'name': unicode,
        'date': date,
        'transport': [{
            '_id': int,
            'carrier': carrier.CarrierCollection,
            'code': unicode,
            'mode': unicode,
            'departure': {
                'station': station.StationCollection,
                'time': datetime
            },
            'arrival': {
                'station': station.StationCollection,
                'time': datetime,
            },
            'price': {
                'value': float,
                'currency': unicode
            },
            'booking': {
                'ref': unicode,
                'url': unicode
            },
            'conditions': unicode
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
