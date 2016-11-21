from collections import OrderedDict

from mongokat import Collection

from .field import Field, process_fields


def find_method(func):
    def wrapped(*args, **kwargs):
        document = func(*args, **kwargs)
        if document:
            document.process('select')
        return document
    return wrapped


def insert_method(func):
    def wrapped(*args, **kwargs):
        args = list(args)
        fields = args[0].document_class.structure
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
        fields = args[0].document_class.structure
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

        initialize_fields(self.document_class.structure.keys(),
                          self.document_class.structure.values())

    def get(self, _id):
        return self.find_one(_id)

    def search(self, fields=None, sort=[], **kwargs):
        if not fields:
            fields = self.document_class.structure.keys()

        query = []
        project = dict(zip(fields, [1 for f in fields]))

        query = [
            {'$project': project}
        ]

        if kwargs:
            query.append({'$match': kwargs})
        if sort:
            query.append({'$sort': OrderedDict(sort)})
        return self.aggregate(query)

    def add(self, fields):
        return self.insert_one(fields).inserted_id

    def upsert(self, fields):
        if '_id' not in fields:
            return self.add(fields)
        else:
            self.update_one({'_id': fields['_id']}, {'$set': fields})
            return fields['_id']
        return False

    def delete(self, _id):
        if self.delete_one({'_id': _id}).deleted_count > 0:
            return True
        return False

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
