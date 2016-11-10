from mongokat import Document


class Document(Document):
    unique = []

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.fields = self.structure.keys()

    def dict(self, fields=None):
        if not fields:
            fields = self.fields

        fields.append('_id')

        return dict(zip(fields, [self[f] for f in fields]))
