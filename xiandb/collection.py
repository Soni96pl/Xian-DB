from collections import OrderedDict

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

    def preprocess_field(self, field):
        name, value = field
        try:
            return (name, self.document_class.preprocessors[name](value))
        except KeyError:
            return (name, value)

    def prepare_document(self, fields):
        fields['_id'] = self.increment()
        fields = dict(map(self.preprocess_field, fields.items()))

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
