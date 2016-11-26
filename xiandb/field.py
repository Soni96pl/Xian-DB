import bcrypt
from bson.dbref import DBRef

from . import document, tools


def get_fields(fields, values, path=None, keys=None, add_missing=True):
    fields = tools.data_get(fields, path=path, keys=keys, force=True)
    if isinstance(fields, list):
        fields = fields[0]

    if add_missing is False and isinstance(fields, dict):
        ret = {}
        for name, field in fields.items():
            if name in values:
                ret[name] = field
    else:
        ret = fields

    return ret


def process_fields(action, fields, values, document=None, path=None,
                   add_missing=True):
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

    keys = tools.path_to_keys(path)
    fields = get_fields(fields, values, keys=keys, add_missing=add_missing)

    if document is None:
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


class Protected(Field):
    def __init__(self, _type):
        super(Protected, self).__init__(_type, default=None, required=True,
                                        unique=False)


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

    def update(self, context, value):
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
        if value is None:
            return None

        value = self.target.get(value.id)
        return super(Reference, self).select(context, value)

    def create(self, context, value):
        if value is None:
            return None
        elif isinstance(value, DBRef):
            pass
        elif isinstance(value, int):
            value = DBRef(self.target_name, value)
        elif isinstance(value, document.Document):
            value.save()
            value = DBRef(self.target_name, value['_id'])
        elif isinstance(value, dict):
            _id = self.target.upsert(value,
                                     _id=value.get('_id', None),
                                     _user=context.get('_user', None))
            assert _id is not False
            value = DBRef(self.target_name, _id)
        return super(Reference, self).create(context, value)

    def update(self, context, value):
        if isinstance(value, DBRef):
            pass
        elif isinstance(value, int):
            value = DBRef(self.target_name, value)
        elif isinstance(value, document.Document):
            value.save()
            value = DBRef(self.target_name, value['_id'])
        elif isinstance(value, dict):
            _id = self.target.upsert(value,
                                     _id=value.get('_id', None),
                                     _user=context.get('_user', None))
            assert _id is not False
            value = DBRef(self.target_name, _id)
        return super(Reference, self).update(context, value)


class Password(Field):
    def __init__(self, required=False):
        super(Password, self).__init__(unicode, default=None,
                                       required=required, unique=False)

    def encrypt(self, value):
        return unicode(bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()))

    def create(self, context, value):
        return super(Password, self).create(context, self.encrypt(value))
