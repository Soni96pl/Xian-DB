from datetime import date, datetime

from xiandb import config
from xiandb.document import Document
from xiandb.collection import Collection
from xiandb.tools import update_dictionary


class TripDocument(Document):
    structure = {
        'user_id': int,
        'name': unicode,
        'date': date,
        'segments': [{
            '_id': int,
            'origin_id': int,
            'destination_id': int,
            'departure': datetime,
            'arrival': datetime,
            'mode': int,
            'carrier': unicode,
            'price': int
        }]
    }

    def get_segment(self, _id):
        try:
            return filter(lambda s: s['_id'] == _id, self['segments'])[0]
        except IndexError:
            return None

    def add_segment(self, segment):
        # Check for a conflicting segment on the same trip
        assert len(filter(lambda e: any([e['departure'] < segment['arrival'],
                                         e['arrival'] > segment['departure']]),
                          self['segments'])) is 0

        segment['_id'] = int(self.collection.system_js.getNextSequence('segmentsid'))

        self['segments'].append(segment)
        self.save()
        return segment['_id']

    def update_segment(self, segment):
        # Check for a conflicting segment on the same trip
        assert len(filter(lambda e: all([
            e['_id'] != segment['_id'],
            any([e['departure'] < segment['arrival'],
                 e['arrival'] > segment['departure']])
        ]), self['segments'])) is 0

        self['segments'] = [update_dictionary(existing, segment) for existing
                            in self['segments']]
        self.save()
        return segment['_id']

    def remove_segment(self, segment_id):
        segment = self.get_segment(segment_id)
        if segment:
            self['segments'] = filter(lambda s: s['_id'] != segment_id,
                                      self['segments'])
            self.save()
            return True
        return False


class TripCollection(Collection):
    __collection__ = 'trips'
    __database__ = config.mongodb['database']
    document_class = TripDocument

    def add(self, user_id, name, date):
        trip = self.find_one({'name': name})
        if trip:
            return False

        return self.insert_one({
            '_id': self.increment(),
            'user_id': user_id,
            'name': name,
            'date': date,
            'segments': []
        })
