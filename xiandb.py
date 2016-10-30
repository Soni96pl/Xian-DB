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
system_js = getattr(client, database).system_js


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
        'email': unicode,
        'favorites': [int]
    }

    def add_favorite(self, city_id):
        if city_id not in self['favorites']:
            self['favorites'].append(city_id)
            return True
        return False

    def remove_favorite(self, city_id):
        if city_id in self['favorites']:
            self['favorites'].remove(city_id)
            return True
        return False


class UserCollection(Collection):
    __collection__ = 'users'
    __database__ = database
    document_class = UserDocument

    def get(self, _id):
        return self.find_one({'_id': _id})

    def signup(self, name, password, email):
        user = self.find_one({'$or': [{'name': name}, {'email': email}]})
        if user:
            return False

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return self.insert_one({
            '_id': system_js.getNextSequence('userid'),
            'name': name,
            'password': hashed,
            'email': email,
            'favorites': []
        })

    def authenticate(self, name, password):
        user = self.find_one({'name': name})
        if not user:
            return False

        password = password.encode('utf-8')
        hashed = user['password'].encode('utf-8')
        if not bcrypt.hashpw(password, hashed):
            return False

        return user


User = UserCollection(client=client)
