from mongokit import Connection, Document
import os

import yaml
from datetime import datetime

with open(os.path.expanduser('~') + "/xian/config.yml", 'r') as config_file:
    cfg = yaml.load(config_file)

connection = Connection(cfg['mongodb']['host'], cfg['mongodb']['port'])
database = cfg['mongodb']['database']


@connection.register
class City(Document):
    __collection__ = 'cities'
    __database__ = database
    structure = {
        'name': unicode,
        'country': unicode,
        'population': int,
        'alternate_names': [unicode],
        'coordinates': [float],
        'story': {
            'content': unicode,
            'updated': datetime,
            'existing': bool
        }
    }
