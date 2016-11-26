from datetime import datetime
from collections import OrderedDict

import pymongo

from ..field import Field, Id
from ..document import Document
from ..collection import Collection


class CityDocument(Document):
    structure = {
        '_id': Id(),
        'name': Field(basestring, required=True),
        'country': Field(basestring, required=True),
        'population': Field(int, required=True),
        'alternate_names': [Field(basestring)],
        'coordinates': [Field(float)],
        'story': {
            'content': Field(basestring),
            'updated': Field(datetime),
            'existing': Field(bool)
        }
    }


class CityCollection(Collection):
    __collection__ = 'cities'
    document_class = CityDocument
