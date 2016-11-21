import bcrypt
from bson.dbref import DBRef

import document


def reduce_fields(fields, values):
    ret = {}
    for name, field in fields.items():
        if name in values:
            ret[name] = field
    return ret


def process_fields(action, fields, values, add_missing=True):
    def break_dictionary(document, fields, values):
        items = []

        for name, field in fields.items():
            if isinstance(field, Field):
                values[name] = values.get(name, None)
            elif type(field) is dict:
                values[name] = values.get(name, {})
            elif type(field) is list:
                values[name] = values.get(name, [])
            else:
                raise ValueError("Field is of incorrect type")

            items.append((name,
                          process_field(document, field, values[name])))

        return dict(items)

    def break_list(document, fields, values):
        field = fields[0]
        return [process_field(document, field, value) for value in values]

    def process_field(document, fields, values):
        if type(fields) is dict:
            return break_dictionary(document, fields, values)
        elif type(fields) is list:
            return break_list(document, fields, values)

        field = fields
        value = values
        return getattr(field, action)(document, value)

    if add_missing is False:
        fields = reduce_fields(fields, values)

    document = values
    processed = process_field(document, fields, values)
    return processed


class Field(object):
    def __init__(self, _type, default=None, required=False, unique=False):
        self.type = _type
        self.assert_type(default)
        self.default = default
        self.required = required
        self.unique = unique

    def initialize(self, name, collection):
        self.name = name
        self.base = collection.base
        self.client = collection.client
        self.database = collection.database
        self.collection = collection

        if self.unique:
            self.collection.collection.create_index(self.name, unique=True)

    def assert_type(self, value):
        if value is not None:
            assert isinstance(value, self.type), \
                "%s: %s(%s)=%s(%s) is of the wrong type!" % (
                    self.collection, self.name, self.type, value, type(value))

    def assert_required(self, value):
        if self.required:
            assert value is not None, \
                "%s: %s is required!" % (self.collection, self.name)

    def default_value(self, value):
        if value is None:
            return self.default
        return value

    def select(self, context, value):
        return value

    def create(self, context, value):
        self.assert_type(value)
        self.assert_required(value)
        value = self.default_value(value)
        return value

    def update(self, context, value):
        self.assert_type(value)
        self.assert_required(value)
        value = self.default_value(value)
        return value


class Id(Field):
    def __init__(self, _type=int, counter_name=None):
        self.counter_name = counter_name

        super(Id, self).__init__(_type, default=None, required=True,
                                 unique=False)

    def initialize(self, name, collection):
        if not self.counter_name:
            self.counter_name = collection.collection.name + 'id'
        super(Id, self).initialize(name, collection)

    @property
    def counter(self):
        return int(self.database.system_js.getNextSequence(self.counter_name))

    def create(self, context, value):
        if value is None:
            value = self.counter

        return super(Id, self).create(context, value)


class Reference(Field):
    def __init__(self, target_name, required=False):
        self.target_name = target_name
        super(Reference, self).__init__(DBRef, default=None, required=required,
                                        unique=False)

    def initialize(self, name, collection):
        super(Reference, self).initialize(name, collection)
        self.target = self.base.collections[self.target_name]

    def select(self, context, value):
        value = self.target.get(value.id)
        return super(Reference, self).select(context, value)

    def create(self, context, value):
        if type(value) is DBRef:
            pass
        elif type(value) is int:
            value = DBRef(self.target_name, value)
        elif type(value) is dict:
            target = self.target(client=self.collection.client)
            _id = target.upsert(value)
            assert _id is not False
            value = DBRef(self.target_name, _id)
        return super(Reference, self).create(context, value)

    def update(self, context, value):
        if type(value) is DBRef:
            pass
        elif type(value) is int:
            value = DBRef(self.target_name, value)
        elif type(value) is dict:
            target = self.target(client=self.collection.client)
            _id = target.upsert(value)
            assert _id is not False
            value = DBRef(self.target_name, _id)
        elif isinstance(value, document.Document):
            value.save()
            value = DBRef(self.target_name, value['_id'])
        return super(Reference, self).update(context, value)


class Password(Field):
    def __init__(self, required=False):
        super(Password, self).__init__(unicode, default=None,
                                       required=required, unique=False)

    def encrypt(self, value):
        return unicode(bcrypt.hashpw(value, bcrypt.gensalt()))

    def create(self, context, value):
        return super(Password, self).create(context, self.encrypt(value))
