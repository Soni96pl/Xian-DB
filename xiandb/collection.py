from collections import OrderedDict

from pymongo.command_cursor import CommandCursor
from mongokat import Collection

from . import tools
from .document import Document
from .field import Field, process_fields


def find_method(func):
    def wrapped(*args, **kwargs):
        fields = args[0].structure
        ret = func(*args, **kwargs)
        if isinstance(ret, Document):
            ret.process('select')
        elif isinstance(ret, CommandCursor):
            ret = list(ret)
            for document in ret:
                process_fields('select', fields, document, add_missing=False)
        return ret
    return wrapped


def insert_method(func):
    def wrapped(*args, **kwargs):
        args = list(args)
        fields = args[0].structure
        if func.__name__ is 'insert_one':
            args[1] = process_fields('create', fields, args[1])
        elif func.__name__ is 'insert_many':
            args[1] = [process_fields('create', fields, values)
                       for values in args[1]]
        elif func.__name__ is 'replace_one':
            args[2] = process_fields('create', fields, args[2])

        return func(*args, **kwargs)
    return wrapped


def update_method(func):
    def wrapped(*args, **kwargs):
        args = list(args)
        fields = args[0].structure
        if func.__name__ is 'update':
            args[2]['$set'] = process_fields('update', fields, args[2]['$set'])
        if func.__name__ in ('update_one', 'update_many'):
            if func.__name__ is 'update_one':
                args[2]['$set'] = process_fields('update',
                                                 fields,
                                                 args[2]['$set'],
                                                 add_missing=False)
            elif func.__name__ is 'update_many':
                args[2]['$set'] = [process_fields('update', fields, values,
                                                  add_missing=False)
                                   for values in args[2]['$set']]

        return func(*args, **kwargs)
    return wrapped


class Collection(Collection):
    def __init__(self, base):
        self.base = base

        self.client = base.database.client
        self.database = base.database
        self.collection = base.database[self.__collection__]

        base.register(self.collection.name, self)

    def initialize(self):
        def initialize_fields(names, fields):
            if isinstance(fields, Field):
                field = fields
                name = names
                field.initialize(name, self)
            elif type(fields) is list:
                map(initialize_fields, names, fields)
            elif type(fields) is dict:
                map(initialize_fields, fields.keys(), fields.values())

        initialize_fields(self.structure.keys(),
                          self.structure.values())

    @property
    def structure(self):
        return self.document_class.structure

    def match(self, _id=None, _user=None, **match):
        if _id:
            match['_id'] = _id
        if _user:
            match['_user'] = _user
        return match

    def get(self, _id, _user=None):
        match = self.match(_id, _user)
        return self.find_one(match)

    def search(self, fields=None, sort=None, path=None, _id=None, _user=None,
               **match):
        if fields is None:
            fields = self.structure.keys()
        if sort is None:
            sort = []

        query = []
        match = self.match(_id, _user, **match)
        project = dict(zip(fields, [1 for f in fields]))

        if match:
            query.append({'$match': match})
        if project:
            query.append({'$project': project})
        if sort:
            query.append({'$sort': OrderedDict(sort)})

        ret = self.aggregate(query)
        if _id is not None and isinstance(_id, int):
            ret = ret[0]
        return tools.data_get(ret, path)

    def add(self, data, _user=None):
        if _user:
            data['_user'] = _user
        return self.insert_one(data).inserted_id

    def patch(self, data, _id, _user=None, path=None):
        match = self.match(_id, _user)
        if path is None:
            if self.update_one(match, {"$set": data}).modified_count == 0:
                return False
        else:
            document = self.find_one(match)
            if document is None:
                return False

            document.update_partial(data, path=path)
            document.save()
        return _id

    def upsert(self, data, _id=None, _user=None, path=None):
        if _id is None:
            return self.add(data, _user)
        return self.patch(data, _id, _user, path)

    def delete(self, _id, _user=None, path=None):
        match = self.match(_id, _user)
        if path is None:
            if self.delete_one(match).deleted_count == 0:
                return False
        else:
            document = self.find_one(match)
            if document is None:
                return False

            document.delete_partial(path=path)
            document.save()
        return True

    @find_method
    def aggregate(self, *args, **kwargs):
        return super(Collection, self).aggregate(*args, **kwargs)

    @find_method
    def find(self, *args, **kwargs):
        return super(Collection, self).find(*args, **kwargs)

    @find_method
    def find_one(self, *args, **kwargs):
        return super(Collection, self).find_one(*args, **kwargs)

    @find_method
    def find_by_id(self, *args, **kwargs):
        return super(Collection, self).find_by_id(*args, **kwargs)

    @find_method
    def find_by_ids(self, *args, **kwargs):
        return super(Collection, self).find_by_ids(*args, **kwargs)

    @find_method
    def find_one_and_delete(self, *args, **kwargs):
        return super(Collection, self).find_one_and_delete(*args, **kwargs)

    @find_method
    def find_one_and_replace(self, *args, **kwargs):
        return super(Collection, self).find_one_and_replace(*args, **kwargs)

    @find_method
    def find_one_and_update(self, *args, **kwargs):
        return super(Collection, self).find_one_and_update(*args, **kwargs)

    @insert_method
    def insert_one(self, *args, **kwargs):
        return super(Collection, self).insert_one(*args, **kwargs)

    @insert_method
    def insert_many(self, *args, **kwargs):
        return super(Collection, self).insert_many(*args, **kwargs)

    @insert_method
    def replace_one(self, *args, **kwargs):
        return super(Collection, self).replace_one(*args, **kwargs)

    @update_method
    def update(self, *args, **kwargs):
        return super(Collection, self).update(*args, **kwargs)

    @update_method
    def update_one(self, *args, **kwargs):
        return super(Collection, self).update_one(*args, **kwargs)

    @update_method
    def update_many(self, *args, **kwargs):
        return super(Collection, self).update_many(*args, **kwargs)

    def save(self, to_save, **kwargs):
        to_save.process('update')
        _id = super(Collection, self).save(to_save, **kwargs)
        to_save.process('select')
        return _id
