import os

import yaml
import bcrypt
from datetime import date, datetime
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


def update_dictionary(existing, new):
    if existing['_id'] != new['_id']:
        return existing

    return new


class Document(Document):
    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.fields = self.structure.keys()

    def dict(self, fields=None):
        if not fields:
            fields = self.fields

        fields.append('_id')

        return dict(zip(fields, [self[f] for f in fields]))


class Collection(Collection):
    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.fields = self.document_class.structure.keys()

    def get(self, _id):
        return self.find_one({'_id': _id})

    def update(self, _id, fields):
        return self.update_one({'_id': _id}, {"$set": fields})

    def delete(self, _id):
        if self.delete_one({'_id': _id}).deleted_count == 1:
            return True
        return False

    def increment(self):
        counter_name = self.__collection__ + 'id'
        return int(system_js.getNextSequence(counter_name))

    def search(self, _id=None, fields=None, sort=[]):
        if not fields:
            fields = self.document_class.structure.keys()

        query = []
        match = {}
        project = dict(zip(fields, [1 for f in fields]))

        query = [
            {'$project': project}
        ]

        if _id is not None:
            match = {'_id': _id}

        if match:
            query.append({'$match': match})
        query.append({'$project': project})
        query.append({'$sort': OrderedDict(sort)})
        return self.aggregate(query)


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


City = CityCollection(client=client)


class UserDocument(Document):
    structure = {
        '_id': int,
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
            '_id': self.increment(),
            'name': name,
            'password': hashed,
            'email': email,
            'favorites': []
        })


User = UserCollection(client=client)


class TripDocument(Document):
    structure = {
        'user_id': int,
        'name': unicode,
        'date': date,
        'segments': [{
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

    def get_segment(self, _id):
        try:
            return filter(lambda s: s['_id'] == _id, self['segments'])[0]
        except IndexError:
            return None

    def add_segment(self, segment):
        assert City.get(segment['origin_id']) is not None
        assert City.get(segment['destination_id']) is not None
        # Check for a conflicting segment on the same trip
        assert len(filter(lambda e: any([e['departure'] < segment['arrival'],
                                         e['arrival'] > segment['departure']]),
                          self['segments'])) is 0

        segment['_id'] = int(system_js.getNextSequence('segmentsid'))

        self['segments'].append(segment)
        self.save()
        return segment['_id']

    def update_segment(self, segment):
        assert City.get(segment['origin_id']) is not None
        assert City.get(segment['destination_id']) is not None
        # Check for a conflicting segment on the same trip
        assert len(filter(lambda e: all([
            e['_id'] != segment['_id'],
            any([e['departure'] < segment['arrival'],
                 e['arrival'] > segment['departure']])
        ]), self['segments'])) is 0

        self['segments'] = [update_dictionary(existing, segment) for existing
                            in self['segments']]
        self.save()
        return segment['_id']

    def remove_segment(self, segment_id):
        segment = self.get_segment(segment_id)
        if segment:
            self['segments'] = filter(lambda s: s['_id'] != segment_id,
                                      self['segments'])
            self.save()
            return True
        return False


class TripCollection(Collection):
    __collection__ = 'trips'
    __database__ = database
    document_class = TripDocument

    def add(self, user_id, name, date):
        trip = self.find_one({'name': name})
        if trip:
            return False

        return self.insert_one({
            '_id': self.increment(),
            'user_id': user_id,
            'name': name,
            'date': date,
            'segments': []
        })


Trip = TripCollection(client=client)
