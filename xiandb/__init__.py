from pymongo import MongoClient

from xiandb import config
from xiandb.models import city, user, trip

client = MongoClient(host=config.mongodb['host'], port=config.mongodb['port'])
City = city.CityCollection(client=client)
User = user.UserCollection(client=client)
Trip = trip.TripCollection(client=client)
Carrier = trip.CarrierCollection(client=client)
Station = trip.StationCollection(client=client)
