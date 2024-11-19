import os
import sys
from datetime import time
import random
import factory
import factory.fuzzy as fuzzy
import random

from factory import Faker, LazyAttribute

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model import db, Base, Client, Parking, ClientParking, is_parking_open

class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    credit_card = factory.LazyAttribute(
        lambda o: None if factory.Faker('boolean') else factory.Faker('credit_card_number'))
    car_number = Faker('text')

class ParkingFactory(factory.Factory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
    address = Faker('address')
    opened = factory.Faker('boolean')
    count_places = factory.Faker('pyint')
    count_available_places = LazyAttribute(lambda obj: random.randint(0, obj.count_places))
    opening_time = factory.LazyFunction(lambda: time(hour=random.randint(5, 9), minute=random.choice([0, 30])))
    closing_time = factory.LazyFunction(lambda: time(hour=random.randint(17, 23), minute=random.choice([0, 30])))
