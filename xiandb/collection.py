from collections import OrderedDict

from mongokat import Collection


class Collection(Collection):
    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.fields = self.document_class.structure.keys()
        self.system_js = self.database.system_js

    def get(self, _id):
        return self.find_one(_id)

    def add(self, fields):
        document = self.prepare_document(fields)
        if not document:
            return False

        return self.insert_one(document).inserted_id

    def update(self, _id, fields):
        if not self.is_unique(fields, _id):
            return False

        return self.update_one({'_id': _id}, {"$set": fields}).acknowledged

    def delete(self, _id):
        if self.delete_one({'_id': _id}).deleted_count > 0:
            return True
        return False

    def increment(self):
        counter_name = self.__collection__ + 'id'
        return int(self.system_js.getNextSequence(counter_name))

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

    def is_unique(self, fields, _id=None):
        query = [
            {field: fields[field]} for field in self.document_class.unique
        ]

        if _id:
            query.append({'$ne': {'_id': _id}})

        if self.find_one(query):
            return False

        return True

    def prepare_document(self, fields):
        if not self.is_unique(fields):
            return False

        fields['_id'] = self.increment()
        for key, value in self.document_class.structure.items():
            if key in fields:
                continue

            if type(value) is dict:
                fields[key] = dict()
            elif type(value) is list:
                fields[key] = list()
            else:
                fields[key] = None

        return fields
