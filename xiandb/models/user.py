import bcrypt

from ..field import Field, Password, Id
from ..document import Document
from ..collection import Collection


class UserDocument(Document):
    structure = {
        '_id': Id(),
        'name': Field(basestring, required=True, unique=True),
        'password': Password(required=True),
        'email': Field(basestring, required=True, unique=True),
        'favorites': [Field(int)]
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
