import os
from typing import List

from numpy import double
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from sqlalchemy import String, Integer, Double, Date
from sqlalchemy import ForeignKey
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
db_root_user = os.environ.get('MARIADB_USER')
db_root_password = os.environ.get('MARIADB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mariadb+mariadbconnector://{db_root_user}:{db_root_password}@db:3306/mydb'
db.init_app(app)


class Client(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(40),nullable=False)
    rides: Mapped[List["Ride"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f'Client(name={self.name})'


class Driver(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(40))
    licensePlate: Mapped[str] = mapped_column(String(20))
    rides: Mapped[List["Ride"]] = relationship(back_populates="driver")


class Ride(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    rideDate: Mapped[Date] = mapped_column(Date)
    distance: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    waypoints: Mapped[List["Waypoint"]] = relationship(back_populates="ride", cascade="all, delete",
                                                       passive_deletes=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("driver.id"),nullable=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"),nullable=True)
    driver: Mapped["Driver"] = relationship(back_populates="rides")
    client: Mapped["Client"] = relationship(back_populates="rides")


class Waypoint(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    number: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[double] = mapped_column(Double)
    longitude: Mapped[double] = mapped_column(Double)
    ride_id: Mapped[int] = mapped_column(ForeignKey('ride.id',ondelete='CASCADE'))
    ride: Mapped["Ride"] = relationship(back_populates="waypoints")


with app.app_context():
    db.create_all()


@app.route("/clients", methods=["GET", "POST", "PUT","PATCH", "DELETE"])
def operations_on_clients():
    if request.method == "GET":
        clients = db.session.query(Client).all()
        return jsonify([{"id": c.id, "name": c.name,"rides":[{"id": r.id} for r in c.rides]} for c in clients]), 200
    elif request.method == "POST":
        client_list = request.get_json(silent=True)
        clients = []
        for client_data in client_list:
            clients.append(Client(name=client_data["name"]))
        db.session.add_all(clients)
        db.session.commit()
        return jsonify([{"id": c.id, "name": c.name,"rides":[{"id": r.id} for r in c.rides]} for c in clients]), 200
    elif request.method == "PUT":
        client_list = request.get_json(silent=True)
        clients = []
        for client_data in client_list:
            client = Client.query.get(client_data["id"])
            client.name = client_data["name"]
            client.rides = client_data["rides"]
            clients.append(client)
        db.session.commit()
        return jsonify([{"id": c.id, "name": c.name,"rides":[{"id": r.id} for r in c.rides]} for c in clients]), 200
    elif request.method == "PATCH":
        client_list = request.get_json(silent=True)
        clients = []
        for client_data in client_list:
            client = Client.query.get(client_data["id"])
            if "name" in client_data:
                client.name = client_data["name"]
            clients.append(client)
            db.session.commit()
        return jsonify([{"id": c.id, "name": c.name,"rides":[{"id": r.id} for r in c.rides]} for c in clients]), 200
    elif request.method == "DELETE":
        client_list = request.get_json(silent=True)
        for client_data in client_list:
            print(client_data["id"])
            db.session.delete(Client.query.get(client_data["id"]))
            db.session.commit()
        return "data deleted",200
    else:
        return "wrong type",404



@app.route("/clients/<client_id>", methods=["GET", "PUT","PATCH", "DELETE"])
def operations_on_client(client_id):
    client = Client.query.get(client_id)
    if client is None:
        return jsonify({"error": "Client not found"}), 404
    else:
        if request.method == "GET":
            return jsonify({"id": client.id, "name": client.name,"rides":[{"id": r.id} for r in client.rides]}), 200
        elif request.method == "PUT":
            client_data = request.get_json()
            client.name=client_data["name"]
            client.rides = client_data["rides"]
            db.session.commit()
            return jsonify({"id": client.id, "name": client.name,"rides":[{"id": r.id} for r in client.rides]}), 200
        elif request.method == "PATCH":
            client_data = request.get_json()
            if "name" in client_data:
                client.name = client_data["name"]
            if "rides" in client_data:
                client.rides = client_data["rides"]
            db.session.commit()
            return jsonify({"id": client.id, "name": client.name,"rides":[{"id": r.id} for r in client.rides]}), 200
        elif request.method == "DELETE":
            db.session.delete(client)
            db.session.commit()
            return "data deleted", 200
        else:
            return "wrong type", 404


@app.route("/rides", methods=["GET", "POST","PUT", "PATCH", "DELETE"])
def operations_on_rides():
    if request.method == "GET":
        rides = db.session.query(Ride).all()
        return jsonify([{"id": r.id, "rideDate": r.rideDate, "distance": r.distance, "price": r.price,"waypoints":[{"id": w.id, "number": w.number, "lat": w.latitude,"long":w.longitude,"ride_id":w.ride_id} for w in r.waypoints]} for r in rides] ), 200
    elif request.method == "POST":
        ride_list = request.get_json()
        rides = []
        for ride_data in ride_list:
            rides.append(Ride(rideDate=ride_data["rideDate"], distance=ride_data["distance"], price=ride_data["price"],driver_id=ride_data["driver_id"],client_id=ride_data["client_id"]))
            db.session.add_all(rides)
            db.session.commit()
        return jsonify([{"id": r.id, "rideDate": r.rideDate, "distance": r.distance, "price": r.price,"waypoints":[{"id": w.id, "number": w.number, "lat": w.latitude,"long":w.longitude,"ride_id":w.ride_id} for w in r.waypoints]} for r in rides]), 200
    elif request.method == "PUT":
        ride_list = request.get_json()
        rides = []
        for ride_data in ride_list:
            ride = Ride.query.get(ride_data["id"])
            ride.rideDate = ride_data["rideDate"]
            ride.distance = ride_data["distance"]
            ride.price = ride_data["price"]
            ride.driver_id = ride_data["driver_id"]
            ride.client_id = ride_data["client_id"]
            rides.append(ride)
            db.session.commit()
        return jsonify([{"id": r.id, "rideDate": r.rideDate, "distance": r.distance, "price": r.price,"waypoints":[{"id": w.id, "number": w.number, "lat": w.latitude,"long":w.longitude,"ride_id":w.ride_id} for w in r.waypoints]} for r in rides]), 200
    elif request.method == "PATCH":
        ride_list = request.get_json()
        rides = []
        for ride_data in ride_list:
            ride = Ride.query.get(ride_data["id"])
            if "rideDate" in ride_data:
                ride.rideDate = ride_data["rideDate"]
            if "distance" in ride_data:
                ride.distance = ride_data["distance"]
            if "price" in ride_data:
                ride.price = ride_data["price"]
            if "driver_id" in ride_data:
                ride.driver_id = ride_data["driver_id"]
            if "client_id" in ride_data:
                ride.client_id = ride_data["client_id"]
            if "waypoints" in ride_data:
                ride.waypoints = ride_data["waypoints"]
            rides.append(ride)
            db.session.commit()
        return jsonify([{"id": r.id, "rideDate": r.rideDate, "distance": r.distance, "price": r.price,"waypoints":[{"id": w.id, "number": w.number, "lat": w.latitude,"long":w.longitude,"ride_id":w.ride_id} for w in r.waypoints]} for r in rides]), 200
    elif request.method == "DELETE":
        ride_list = request.get_json()
        for ride_data in ride_list:
            ride = Ride.query.get(ride_data["id"])
            db.session.delete(ride)
            db.session.commit()
        return "data deleted", 200
    else:
        return "wrong type", 404


@app.route("/rides/<ride_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def operations_on_ride(ride_id):
    ride = Ride.query.get(ride_id)
    if ride is None:
        return "Ride not found", 404
    else:
        if request.method == "GET":
            return jsonify({"id": ride.id, "rideDate": ride.rideDate,"distance": ride.distance,"price": ride.price,"driver_id":ride.driver_id,"client_id":ride.client_id,"waypoints":[{"id": w.id, "number": w.number, "lat": w.latitude,"long":w.longitude,"ride_id":w.ride_id} for w in ride.waypoints]}), 200
        elif request.method == "PUT":
            ride_data = request.get_json()
            ride.rideDate = ride_data["rideDate"]
            ride.distance = ride_data["distance"]
            ride.price = ride_data["price"]
            ride.driver_id = ride_data["driver_id"]
            ride.client_id = ride_data["client_id"]
            ride.waypoints = ride_data["waypoints"]
            db.session.commit()
            return jsonify({"id": ride.id, "rideDate": ride.rideDate,"distance": ride.distance,"price": ride.price,"driver_id":ride.driver_id,"client_id":ride.client_id}), 200
        elif request.method == "PATCH":
            ride_data = request.get_json()
            if "rideDate" in ride_data:
                ride.rideDate = ride_data["rideDate"]
            if "distance" in ride_data:
                ride.distance = ride_data["distance"]
            if "price" in ride_data:
                ride.price = ride_data["price"]
            if "driver_id" in ride_data:
                ride.driver_id = ride_data["driver_id"]
            if "client_id" in ride_data:
                ride.client_id = ride_data["client_id"]
            db.session.commit()
            return jsonify({"id": ride.id, "rideDate": ride.rideDate, "distance": ride.distance, "price": ride.price,"driver_id": ride.driver_id, "client_id": ride.client_id}), 200
        elif request.method == "DELETE":
            db.session.delete(ride)
            db.session.commit()
            return "data deleted", 200
        else:
            return "wrong type", 404


@app.route("/rides/<ride_id>/waypoints", methods=["GET","POST", "PUT", "PATCH", "DELETE"])
def operations_on_ride_waypoints(ride_id):
    if request.method == "GET":
        waypoints = db.session.query(Waypoint).filter_by(ride_id=ride_id).all()
        return jsonify([{"id": w.id, "number": w.number, "lat": w.latitude,"long":w.longitude,"ride_id":w.ride_id} for w in waypoints]), 200
    elif request.method == "POST":
        waypoint_list = request.get_json()
        waypoints = []
        for waypoint_data in waypoint_list:
            waypoints.append(Waypoint(number=waypoint_data["number"],latitude=waypoint_data["latitude"],longitude=waypoint_data["longitude"],ride_id=ride_id))
        db.session.add_all(waypoints)
        db.session.commit()
        return jsonify(
            [{"id": w.id, "number": w.number, "latitude": w.latitude, "longitude": w.longitude, "ride_id": w.ride_id} for w in
             waypoints]), 200
    elif request.method == "PUT":
        waypoint_list = request.get_json()
        waypoints = []
        for waypoint_data in waypoint_list:
            waypoint = Waypoint.query.get(waypoint_data["id"])
            waypoint.number = waypoint_data["number"]
            waypoint.latitude = waypoint_data["latitude"]
            waypoint.longitude = waypoint_data["longitude"]
            waypoint.ride_id = waypoint_data["ride_id"]
            waypoints.append(waypoint)
            db.session.commit()
        return jsonify(
            [{"id": w.id, "number": w.number, "latitude": w.latitude, "longitude": w.longitude, "ride_id": w.ride_id}
             for w in
             waypoints]), 200
    elif request.method == "PATCH":
        waypoint_list = request.get_json()
        waypoints = []
        for waypoint_data in waypoint_list:
            waypoint = Waypoint.query.get(waypoint_data["id"])
            if "number" in waypoint_data:
                waypoint.number = waypoint_data["number"]
            if "latitude" in waypoint_data:
                waypoint.latitude = waypoint_data["latitude"]
            if "longitude" in waypoint_data:
                waypoint.longitude = waypoint_data["longitude"]
            if "ride_id" in waypoint_data:
                waypoint.ride_id = waypoint_data["ride_id"]
            waypoints.append(waypoint)
            db.session.commit()
        return jsonify(
            [{"id": w.id, "number": w.number, "latitude": w.latitude, "longitude": w.longitude, "ride_id": w.ride_id}
             for w in
             waypoints]), 200
    elif request.method == "DELETE":
        waypoint_list = request.get_json()
        for waypoint_data in waypoint_list:
            waypoint = Waypoint.query.get(waypoint_data["id"])
            db.session.delete(waypoint)
            db.session.commit()
        return "data deleted", 200
    else:
        return "wrong type", 404

@app.route("/drivers", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def operations_on_drivers():
    if request.method == "GET":
        drivers = db.session.query(Driver).all()
        return jsonify([{"id": d.id, "name": d.name,"licensePlate":d.licensePlate, "rides":[{"id": r.id} for r in d.rides]} for d in drivers]), 200
    elif request.method == "POST":
        driver_list = request.get_json()
        drivers = []
        for driver_data in driver_list:
            drivers.append(Driver(name=driver_data["name"],licensePlate=driver_data["licensePlate"]))
        db.session.add_all(drivers)
        db.session.commit()
        return jsonify([{"id": d.id, "name": d.name,"licensePlate":d.licensePlate,"rides":[{"id": r.id} for r in d.rides]} for d in drivers]), 200
    elif request.method == "PUT":
        driver_list = request.get_json()
        drivers = []
        for driver_data in driver_list:
            driver = Driver.query.get(driver_data["id"])
            driver.name = driver_data["name"]
            driver.licensePlate = driver_data["licensePlate"]
            driver.rides = driver_data["rides"]
            drivers.append(driver)
            db.session.commit()
        return jsonify([{"id": d.id, "name": d.name,"licensePlate":d.licensePlate, "rides":[{"id": r.id} for r in d.rides]} for d in drivers]), 200
    elif request.method == "PATCH":
        driver_list = request.get_json()
        drivers = []
        for driver_data in driver_list:
            driver = Driver.query.get(driver_data["id"])
            if "name" in driver_data:
                driver.name = driver_data["name"]
            if "licensePlate" in driver_data:
                driver.licensePlate = driver_data["licensePlate"]
            if "rides" in driver_data:
                driver.rides = driver_data["rides"]
            drivers.append(driver)
            db.session.commit()
        return jsonify([{"id": d.id, "name": d.name,"licensePlate":d.licensePlate, "rides": [{"id": r.id} for r in d.rides]} for d in drivers]), 200
    elif request.method == "DELETE":
        driver_list = request.get_json()
        for driver_data in driver_list:
            db.session.delete(Driver.query.get(driver_data["id"]))
            db.session.commit()
        return "data deleted", 200
    else:
        return "wrong type", 404


@app.route("/drivers/<driver_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def operations_on_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if driver is None:
        return "Driver not found", 404
    else:
        if request.method == "GET":
            return jsonify({"id": driver.id, "name": driver.name,"licensePlate":driver.licensePlate, "rides":[{"id": r.id} for r in driver.rides]}), 200
        elif request.method == "PUT":
            driver_data = request.get_json()
            driver.name = driver_data["name"]
            driver.licensePlate = driver_data["licensePlate"]
            driver.rides = driver_data["rides"]
            db.session.commit()
            return jsonify({"id": driver.id, "name": driver.name, "rides":[{"id": r.id} for r in driver.rides]}), 200
        elif request.method == "PATCH":
            driver_data = request.get_json()
            if  "name" in driver_data:
                driver.name = driver_data["name"]
            if "licensePlate" in driver_data:
                driver.licensePlate = driver_data["licensePlate"]
            if "rides" in driver_data:
                driver.rides = driver_data["rides"]
            db.session.commit()
            return jsonify({"id": driver.id, "name": driver.name, "rides":[{"id": r.id} for r in driver.rides]}), 200
        elif request.method == "DELETE":
            db.session.delete(driver)
            db.session.commit()
            return "data deleted", 200
        else:
            return "wrong type", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
