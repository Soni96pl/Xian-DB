from mongokat import Collection, Document
from pymongo import MongoClient
import os

import yaml
from datetime import datetime

with open(os.path.expanduser('~') + "/xian/config.yml", 'r') as config_file:
    cfg = yaml.load(config_file)

client = MongoClient(host=cfg['mongodb']['host'], port=cfg['mongodb']['port'])
database = cfg['mongodb']['database']


class CityDocument(Document):
    structure = {
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
    __database__ = database
    document_class = CityDocument


City = CityCollection(client=client)
