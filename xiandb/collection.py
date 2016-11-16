from collections import OrderedDict
from inspect import isclass

from bson.dbref import DBRef
from mongokat import Collection


class Collection(Collection):
    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.fields = self.document_class.structure.keys()
        self.system_js = self.database.system_js

    def get(self, _id):
        return self.find_one(_id)

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

    def delete(self, _id):
        if self.delete_one({'_id': _id}).deleted_count > 0:
            return True
        return False

    def increment(self):
        counter_name = self.__collection__ + 'id'
        return int(self.system_js.getNextSequence(counter_name))

    def is_unique(self, fields, _id=None):
        query = [
            {field: fields[field]} for field in self.document_class.unique
        ]

        if _id:
            query.append({'$ne': {'_id': _id}})

        if self.find_one(query):
            return False

        return True

    def preprocess_fields(self, fields):
        def preprocess_level(preprocessor, f):
            name, value = f
            try:
                p = preprocessor[name]
                if type(value) is dict:
                    return (name, dict(map(lambda f: preprocess_level(p, f),
                                           value.items())))
                elif type(value) is list:
                    return (name, map(lambda f: preprocess_level(p, f),
                                      value))
                else:
                    return (name, p(value))
            except KeyError:
                return (name, value)

        return dict(map(
            lambda f: preprocess_level(self.document_class.preprocessors, f),
            fields.items()
        ))

    def prepare_document(self, fields):
        fields['_id'] = self.increment()
        fields = self.preprocess_fields(fields)

        def merge_dictionary(structure, fields):
            items = []

            for name, value in structure.items():
                if name not in fields:
                    if type(value) in [dict, Collection]:
                        fields[name] = {}
                    elif type(value) is list:
                        fields[name] = []
                    else:
                        fields[name] = None

                items.append((name, merge_structure(value, fields[name])))
            return dict(items)

        def merge_structure(structure, fields):
            if type(structure) is dict:
                return merge_dictionary(structure, fields)
            elif type(structure) is list:
                return [merge_structure(structure[0], f) for f in fields]
            elif isclass(structure) and issubclass(structure, Collection):
                collection = structure(client=self.client)
                _id = collection.upsert(fields)
                if not _id:
                    return False

                return DBRef(structure.__collection__, _id)
            return fields

        return merge_structure(self.document_class.structure, fields)

    def add(self, fields):
        if not self.is_unique(fields):
            return False

        document = self.prepare_document(fields)
        return self.insert_one(document).inserted_id

    def update(self, _id, fields):
        if not self.is_unique(fields, _id):
            return False

        return self.update_one({'_id': _id}, {"$set": fields}).acknowledged

    def upsert(self, fields):
        if '_id' not in fields:
            return self.add(fields)
        elif self.update(fields['_id'], fields):
            return fields['_id']
        return False
