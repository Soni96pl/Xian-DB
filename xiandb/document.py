from mongokat import Document

import field
import tools


class Document(Document):
    def __init__(self, doc=None, mongokat_collection=None, fetched_fields=None,
                 gen_skel=None):
        super(Document, self).__init__(doc, mongokat_collection,
                                       fetched_fields, gen_skel)

        self.database = self.mongokat_collection.database
        self.client = self.mongokat_collection.client

    def save(self, force=False, uuid=False, *args, **kwargs):
        if not self._initialized_with_doc and not force:
            raise Exception("Cannot save a document not initialized from a \
                             Python dict. This might remove fields from the \
                             DB!")

        return self.mongokat_collection.save(self, **kwargs)

    def update_partial(self, values, path):
        self.process('update', values=values, path=path, add_missing=False)

    def delete_partial(self, path):
        document = tools.data_remove(self, path)
        for name, value in document.items():
            self[name] = value

    def process(self, action, fields=None, values=None, path=None,
                add_missing=True):
        if values is None:
            values = self

        if fields is None:
            fields = self.structure

        processed = field.process_fields(action, fields, values, document=self,
                                         path=path, add_missing=add_missing)

        document = tools.data_update(self, processed, path)
        for name, value in document.items():
            self[name] = value
        return self
