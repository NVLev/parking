import json
import os
import sys

import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.model import Base, Client, Parking, ClientParking

@pytest.mark.parametrize("route", ["/clients/1",
                                   "/clients"])
def test_route_status(app_client, route):
    rv = app_client.get(route)
    assert rv.status_code == 200

def test_create_client(app_client) -> None:
    client_data = {"name": "Pirjo", "surname": "Myryläinen",
                 "credit_card": "1234567891", "car_number": "FC123KL"}
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/clients/add_client", json=client_data, headers=headers)

    assert resp.status_code == 201

def test_create_parking(app_client) -> None:
    parking_data = {"address": "123 Aleksanderkatu, Helsinki", "opened": True,
                 "count_places": 20, "count_available_places": 18,
                   "opening_time": "07:00", "closing_time": "21:00"}
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/parking/add_parking", json=parking_data, headers=headers)
    assert resp.status_code == 201


def test_check_in_parking(app_client, db) -> None:
    check_in_data = {"client_id": 1,
                     "parking_id": 1,
                     "time_in": "08:00"}
    # client = db.session.get(Client(1))
    parking= db.session.get(Parking, 1)
    before = parking.count_available_places
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/client_parkings", json=check_in_data, headers=headers)
    assert resp.status_code == 201
    after = parking.count_available_places
    assert before - after == 1
    assert parking.opened == True

def test_check_in_parking_full(app_client, db):
    client = Client(id=3, credit_card="1234-5678-9012-3456")
    parking = Parking(id=4, address="Test Address", count_available_places=0, opened=True)
    db.session.add(client)
    db.session.add(parking)
    db.session.commit()

    check_in_data = {
        "client_id": 3,
        "parking_id": 4
    }

    resp = app_client.post("/client_parkings", json=check_in_data)


    assert resp.status_code == 400
    assert resp.json["error"] == "No available parking spaces"

    updated_parking = db.session.query(Parking).get(4)
    assert updated_parking.count_available_places == 0

    client_parking = db.session.query(ClientParking).filter_by(client_id=3, parking_id=4).first()
    assert client_parking is None

def test_check_out_parking(app_client, db) -> None:
    check_out_data = {
        "client_id": 1,
        "parking_id": 2,
        "time_out": "10:00"
    }
    client = db.session.get(Client(1))
    assert client.credit_card is not None
    parking = db.session.get(Parking(2))
    before = parking.count_available_places
    resp = app_client.delete("/check_out_parkings", json=check_out_data)
    assert resp.status_code == 200
    assert resp.json["message"] == "Check-out completed successfully"
    after = parking.count_available_places
    assert after - before == 1