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
        if len(filter(lambda e: any([e['departure'] < segment['arrival'],
                                     e['arrival'] > segment['departure']]),
                      self['segments'])) > 0:
            return False

        segment['_id'] = int(self.collection.system_js.getNextSequence('segmentsid'))

        self['segments'].append(segment)
        return segment['_id']

    def update_segment(self, segment):
        # Check for a conflicting segment on the same trip
        if len(filter(lambda e: all([
            e['_id'] != segment['_id'],
            any([e['departure'] < segment['arrival'],
                 e['arrival'] > segment['departure']])
        ]), self['segments'])) > 0:
            return False

        self['segments'] = [update_dictionary(existing, segment) for existing
                            in self['segments']]
        return True

    def remove_segment(self, segment_id):
        segment = self.get_segment(segment_id)
        if segment:
            self['segments'] = filter(lambda s: s['_id'] != segment_id,
                                      self['segments'])
            return True
        return False


class TripCollection(Collection):
    __collection__ = 'trips'
    __database__ = config.mongodb['database']
    document_class = TripDocument

    def add(self, trip):
        trip = self.find_one({'name': trip['name']})
        if trip:
            return False

        trip['_id'] = self.increment()
        return self.insert_one(trip).inserted_id
