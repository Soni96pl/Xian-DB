import os

import yaml
import bcrypt
from datetime import datetime

from mongokat import Collection, Document
from pymongo import MongoClient

try:
    with open(os.path.expanduser('~') + '/xian/config.yml', 'r') as cfg_file:
        cfg = yaml.load(cfg_file)
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

    def signup(self, name, password, email):
        user = self.find_one({'$or': [{'name': name}, {'email': email}]})
        if user:
            return False

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return self.insert_one({
            'name': name,
            'password': hashed,
            'email': email
        })

User = UserCollection(client=client)
