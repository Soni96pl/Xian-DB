from mongokat import Document

import field


class Document(Document):
    def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None,
                 gen_skel=None):
        super(Document, self).__init__(doc, mongokat_collection,
                                       fetched_fields, gen_skel)

        self.database = self.mongokat_collection.database
        self.client = self.mongokat_collection.client

    def get_sub(self, name, _id):
        try:
            return filter(lambda s: s['_id'] == _id, self[name])[0]
        except IndexError:
            return None

    def increment_sub(self, name):
        counter_name = name + 'id'
        return int(self.database.system_js.getNextSequence(counter_name))

    def add_sub(self, name, fields):
        fields['_id'] = self.increment_sub(name)
        self[name].append(fields)
        return fields['_id']

    def update_sub(self, name, _id, fields):
        fields['_id'] = _id
        self[name] = [e if e['_id'] is not fields['_id'] else fields
                      for e in self[name]]
        return True

    def remove_sub(self, name, _id):
        sub = self.get_sub(name, _id)
        if not sub:
            return False

        self[name] = filter(lambda s: s['_id'] != _id, self[name])
        return True

    def save(self, force=False, uuid=False, *args, **kwargs):
        if not self._initialized_with_doc and not force:
            raise Exception("Cannot save a document not initialized from a \
                             Python dict. This might remove fields from the \
                             DB!")

        return self.mongokat_collection.save(self, **kwargs)

    def process(self, action, fields=None, values=None, add_missing=True):
        if values is None:
            values = self

        if fields is None:
            fields = self.structure

        processed = field.process_fields(action, fields, values, add_missing)
        for name, value in processed.items():
            self[name] = value
        return self
