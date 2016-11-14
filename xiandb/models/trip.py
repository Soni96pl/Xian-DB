from datetime import date, datetime

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection


class TripDocument(Document):
    structure = {
        'user_id': int,
        'name': unicode,
        'date': date,
        'transport': [{
            '_id': int,
            'origin_id': int,
            'destination_id': int,
            'departure': datetime,
            'arrival': datetime,
            'mode': int,
            'carrier': unicode,
            'price': int
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
