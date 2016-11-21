from . import config
from .base import Base
from .models import city, user, trip, carrier, station


base = Base(config.mongodb['host'], config.mongodb['port'],
            config.mongodb['database'])

City = city.CityCollection(base)
User = user.UserCollection(base)
Trip = trip.TripCollection(base)
Carrier = carrier.CarrierCollection(base)
Station = station.StationCollection(base)

base.initialize(create_indexes=True)
