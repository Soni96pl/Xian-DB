import os

import yaml
import bcrypt
from datetime import datetime
from collections import OrderedDict

from mongokat import Collection, Document
import pymongo
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


class Document(Document):
    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.fields = self.structure.keys()


class Collection(Collection):
    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.fields = self.document_class.structure.keys()

    def get(self, _id):
        return self.find_one({'_id': _id})


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

    def search(self, _id=None, name=None, fields=None, sort=[]):
        if not fields:
            fields = self.document_class.structure.keys()

        project = dict(zip(fields, [1 for x in fields]))

        query = [
            {'$match': None},
            {'$project': project}
        ]

        if _id:
            query[0]['$match'] = {'_id': _id}
        else:
            query[0]['$match'] = {'$or': [
                {'name': name},
                {'alternate_names': name.lower()}
            ]}
            query[1]['$project']['nameMatch'] = {'$eq': ['$name', name]}
            sort.insert(0, ('nameMatch', pymongo.DESCENDING))

        query.append({'$sort': OrderedDict(sort)})
        return self.aggregate(query)


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

    def authenticate(self, name, password):
        user = self.find_one({'name': name})
        if not user:
            return False

        password = password.encode('utf-8')
        hashed = user['password'].encode('utf-8')
        if not bcrypt.hashpw(password, hashed):
            return False

        return user

    def add(self, name, password, email):
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


User = UserCollection(client=client)
