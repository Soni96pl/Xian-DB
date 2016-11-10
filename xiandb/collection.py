from collections import OrderedDict

from mongokat import Collection


class Collection(Collection):
    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.fields = self.document_class.structure.keys()
        self.system_js = self.database.system_js

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
