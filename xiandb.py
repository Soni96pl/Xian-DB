from mongokat import Collection, Document
from pymongo import MongoClient
import os

import yaml
from datetime import datetime

try:
    with open(os.path.expanduser('~') + '/xian/config.yml', 'r') as config_file:
        cfg = yaml.load(config_file)
except IOError:
    print "Couldn't find a valid configuration file in ~/xian/config.xml"
    print "Please refer to README.rst"

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


class UserDocument(Document):
    structure = {
        'name': unicode,
        'password': unicode,
        'email': unicode
    }


class UserCollection(Collection):
    __collection__ = 'users'
    __database__ = database
    document_class = UserDocument


User = UserCollection(client=client)
