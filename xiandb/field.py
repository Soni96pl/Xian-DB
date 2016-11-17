from bson.dbref import DBRef


class Field(object):
    def __init__(self, type, default=None, required=False, unique=False,
                 oncreate=None, onupdate=None, onselect=None):
        self.type = type
        self.assert_type(default)
        self.default = default
        self.required = required
        self.unique = unique
        self._oncreate = oncreate if oncreate else lambda s, v: v
        self._onupdate = onupdate if onupdate else lambda s, v: v
        self._onselect = onselect if onselect else lambda s, v: v

    def register(self, name, collection):
        self.name = name
        self.database = collection.database
        self.collection = collection
        self.document = self.collection.document_class

    def assert_type(self, value):
        if value is not None:
            assert isinstance(value, self.type)

    def assert_required(self, value):
        if self.required:
            assert value is not None, \
                "%s: %s is required!" % (self.collection, self.name)

    def assert_unique(self, value):
        if self.unique and value is not self.default:
            assert self.collection.find_one({self.name: value}) is None, \
                "%s: %s is not unique!" % (self.collection, self.name)

    def default_value(self, value):
        if value is None:
            return self.default
        return value

    def oncreate(self, value):
        self.assert_type(value)
        self.assert_required(value)
        value = self.default_value(value)
        self.assert_unique(value)
        return self._oncreate(self, value)

    def onupdate(self, value):
        return self._onupdate(self, value)

    def onselect(self, value):
        return self._onselect(self, value)


class Id(Field):
    def __init__(self, type=int, counter=None, oncreate=None, onupdate=None,
                 onselect=None):
        self.counter = counter

        super(Id, self).__init__(type, None, True, True, oncreate, onupdate,
                                 onselect)

    def register(self, name, collection):
        if not self.counter:
            self.counter = collection.__collection__ + 'id'

        return super(Id, self).register(name, collection)

    def oncreate(self, value=None):
        if value is None:
            value = int(self.database.system_js.getNextSequence(self.counter))

        return super(Id, self).oncreate(value)


class Reference(Field):
    def __init__(self, target, required=False):
        self.target = target
        self.target_name = target.__collection__
        super(Reference, self).__init__(DBRef, None, required, False)

    def oncreate(self, value):
        if type(value) is DBRef:
            pass
        elif type(value) is int:
            value = DBRef(self.target_name, value)
        elif type(value) is dict:
            target = self.target(client=self.collection.client)
            _id = target.upsert(value)
            assert _id is not False
            value = DBRef(self.target_name, _id)
        return super(Reference, self).oncreate(value)

    def onupdate(self, value):
        target = self.target(client=self.collection.client)
        _id = target.upsert(value)
        assert _id is not False
        value = DBRef(self.target_name, _id)
        return super(Reference, self).oncreate(value)
