from collections import OrderedDict
from inspect import isclass

from mongokat import Collection

from xiandb.field import Field


class Collection(Collection):
    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.register_fields(self.document_class.structure.keys(),
                             self.document_class.structure.values())

    def register_fields(self, name, fields):
        if isinstance(fields, Field):
            fields.register(name, self)
        elif type(fields) is list:
            map(self.register_fields, name, fields)
        elif type(fields) is dict:
            map(self.register_fields, fields.keys(), fields.values())

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
        counter = self.__collection__ + 'id'
        return int(self.database.system_js.getNextSequence(counter))

    def prepare_document(self, fields):
        def merge_dictionary(structure, fields):
            items = []

            for name, field in structure.items():
                if isinstance(field, Field):
                    fields[name] = fields.get(name, None)
                elif type(field) is dict:
                    fields[name] = fields.get(name, {})
                elif type(field) is list:
                    fields[name] = fields.get(name, [])
                else:
                    raise ValueError("Field is of incorrect type")

                items.append((name, merge_structure(field, fields[name])))
            return dict(items)

        def merge_list(structure, fields):
            field = structure[0]
            return [merge_structure(field, value) for value in fields]

        def merge_structure(structure, fields):
            if type(structure) is dict:
                return merge_dictionary(structure, fields)
            elif type(structure) is list:
                return merge_list(structure, fields)

            field = structure
            value = fields
            return field.oncreate(value)

        return merge_structure(self.document_class.structure, fields)

    def add(self, fields):
        document = self.prepare_document(fields)
        print document
        return self.insert_one(document).inserted_id

    def update(self, _id, fields):
        return self.update_one({'_id': _id}, {"$set": fields}).acknowledged

    def upsert(self, fields):
        if '_id' not in fields:
            return self.add(fields)
        elif self.update(fields['_id'], fields):
            return fields['_id']
        return False
