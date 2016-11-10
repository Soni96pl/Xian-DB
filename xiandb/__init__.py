from pymongo import MongoClient

from xiandb import config
from xiandb.models import city, user, trip

client = MongoClient(host=config.mongodb['host'], port=config.mongodb['port'])
database = config.mongodb['database']


City = city.CityCollection(client=client)
User = user.UserCollection(client=client)
Trip = trip.TripCollection(client=client)
