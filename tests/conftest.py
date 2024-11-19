import os
import sys
from datetime import datetime, date
import pytest
from flask import template_rendered
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from application.app import create_app
from models.model import db as _db
from config import Config
from models.model import Base, Client, Parking, ClientParking, is_parking_open


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
    with _app.app_context():
        _db.create_all()
        today = date.today()
        client = Client(id = 1,
                        name='test_name',
                       surname='test_surname',
                       credit_card='1234567899',
                       car_number='ABC123HK')
        _db.session.add(client)
        _db.session.flush()

        parking = Parking(id = 1,
                            address='address',
                          opened=True,
                          count_places=10,
                          count_available_places=10,
                          opening_time="06:00",
                          closing_time="21:00"
                          )
        _db.session.add(parking)
        _db.session.flush()

        client_parking = ClientParking(
            id=1,
            client_id=client.id,
            parking_id=parking.id,
            time_in=datetime.combine(today, datetime.strptime("07:00", "%H:%M").time()),
            time_out=datetime.combine(today, datetime.strptime("09:00", "%H:%M").time())
        )
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app
        _db.session.remove()
        _db.session.commit()
        _db.drop_all()

@pytest.fixture
def app_client(app):
    app_client = app.test_client()
    yield app_client

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db