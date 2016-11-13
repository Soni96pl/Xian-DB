from mongokat import Document


class Document(Document):
    unique = []
    validators = {'self': []}
    preprocessors = {}

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.fields = self.structure.keys()

    def dict(self, fields=None):
        if not fields:
            fields = self.fields

        fields.append('_id')

        return dict(zip(fields, [self[f] for f in fields]))

    def get_sub(self, name, _id):
        try:
            return filter(lambda s: s['_id'] == _id, self[name])[0]
        except IndexError:
            return None

    def increment_sub(self, name):
        counter_name = name + 'id'
        return int(self.mongokat_collection.system_js.getNextSequence(counter_name))

    def validate_sub(self, name, fields):
        return all([v(fields) for v in self.validators[name]])

    def add_sub(self, name, fields):
        if not self.validate_sub(name, fields):
            return False

        fields['_id'] = self.increment_sub(name)
        self[name].append(fields)
        return fields['_id']

    def update_sub(self, name, _id, fields):
        fields['_id'] = _id
        if not self.validate_sub(name, fields):
            return False

        self[name] = [e if e['_id'] is not fields['_id'] else fields
                      for e in self[name]]
        return True

    def remove_sub(self, name, _id):
        sub = self.get_sub(name, _id)
        if not sub:
            return False

        self[name] = filter(lambda s: s['_id'] != _id, self[name])
        return True
