from pymongo import MongoClient


class Base(object):
    initialized = False

    def __init__(self, host, port, database):
        self.client = MongoClient(host=host, port=port)
        self.database = self.client[database]
        self.collections = {}

    def register(self, name, collection):
        if self.initialized:
            raise Exception("Can't register new collections after database has \
                             been initialized")

        self.collections[name] = collection

    def initialize(self, create_indexes):
        for name, collection in self.collections.items():
            collection.initialize()
        self.initialized = True
