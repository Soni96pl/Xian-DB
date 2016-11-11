import bcrypt

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection


class UserDocument(Document):
    structure = {
        '_id': int,
        'name': unicode,
        'password': unicode,
        'email': unicode,
        'favorites': [int]
    }
    preprocessors = {
        'password': lambda p: unicode(bcrypt.hashpw(p, bcrypt.gensalt()))
    }
    unique = ['name', 'email']

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
    __database__ = config.mongodb['database']
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
