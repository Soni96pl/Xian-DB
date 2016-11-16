from datetime import datetime
from collections import OrderedDict

import pymongo

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection


class CityDocument(Document):
    structure = {
        '_id': int,
        'name': unicode,
        'country': unicode,
        'population': int,
        'alternate_names': [unicode],
        'coordinates': [float],
        'story': {
            'content': unicode,
            'updated': datetime,
            'existing': bool
        }
    }


class CityCollection(Collection):
    __collection__ = 'cities'
    __database__ = config.mongodb['database']
    document_class = CityDocument

    def search(self, _id=None, name=None, fields=None, sort=[]):
        if not fields:
            fields = self.document_class.structure.keys()

        query = []
        match = {}
        project = dict(zip(fields, [1 for f in fields]))

        if _id is not None:
            match = {'_id': _id}
        elif name is not None:
            match = {'$or': [
                {'name': name},
                {'alternate_names': name.lower()}
            ]}
            project['nameMatch'] = {'$eq': ['$name', name]}
            sort.insert(0, ('nameMatch', pymongo.DESCENDING))

        if match:
            query.append({'$match': match})
        query.append({'$project': project})
        query.append({'$sort': OrderedDict(sort)})
        return self.aggregate(query)
