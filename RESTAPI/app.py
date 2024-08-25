from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text
from flask_marshmallow import Marshmallow
import datetime
from datetimerange import DateTimeRange
from flask_cors import CORS, cross_origin
import os

## Setting up the app
app = Flask(__name__)
CORS(app)

## Setting up SQLAlchemy
basedir = os.getcwd() ## the path for the application itself
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(basedir, 'booking.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

## Adding CLI Command for DB creation and deletion
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')

@app.cli.command('db_seed')
def db_seed():
    pass

## Creating API

## Default Route
@app.route('/')
def home():
    return jsonify(message='Booking API')

## Add Appointments
@app.route('/add_appointments', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def add_appointment():
    date = request.json['date']
    time_from = request.json['time_from']
    time_to = request.json['time_to']

    if not date or not time_from or not time_to:
        return jsonify(message='Date and time cannot be blank'), 406

    date_time_from = datetime.datetime.strptime(f'{date}-{time_from}', '%Y-%m-%d-%H:%M')
    date_time_to = datetime.datetime.strptime(f'{date}-{time_to}', '%Y-%m-%d-%H:%M')
    received_dates = DateTimeRange(f'{date}T{time_from}', f'{date}T{time_to}')

    if datetime.datetime.now() > date_time_from:
        return jsonify(message='Any booking for the past dates or time cannot be accommodated'), 406
    if date_time_from > date_time_to:
        return jsonify(message='End time must be after start time'), 406

    if datetime.datetime.strptime(date, '%Y-%m-%d').weekday() == 6:
        return jsonify(message='Sorry, appointments are only allowed from Monday to Saturday'), 406

    opening_hours = DateTimeRange(f'{date}T09:00', f'{date}T17:00')
    if not (received_dates in opening_hours):
        return jsonify(message='Appointments are only allowed from 9:00 AM - 5:00 PM'), 406

    success_message = 'You added a new record!'
    datas = Appointment.query.all()
    if datas:
        for data in datas:
            data_dates = DateTimeRange(str(data.date_time_from).replace(' ', 'T'), str(data.date_time_to).replace(' ', 'T'))
            if data_dates.is_intersection(received_dates):
                return jsonify(message='There is a conflict between your schedule'), 409

    new_appointment = Appointment(
        first_name=request.json['first_name'],
        last_name=request.json['last_name'],
        comments=request.json['comments'],
        date_time_from=date_time_from,
        date_time_to=date_time_to
    )

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify(message=success_message), 201

## Updating Appointments
@app.route('/update_appointments/<int:id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def update_appointments(id: int):
    record = Appointment.query.filter_by(id=id).first()
    if record:
        data = request.json
        date = data['date']
        time_from = data['time_from']
        time_to = data['time_to']

        if not date or not time_from or not time_to:
            return jsonify(message='Date and time cannot be blank'), 406

        try:
            date_time_from = datetime.datetime.strptime(f'{date}T{time_from}', '%Y-%m-%dT%H:%M:%S')
            date_time_to = datetime.datetime.strptime(f'{date}T{time_to}', '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            date_time_from = datetime.datetime.strptime(f'{date}T{time_from}', '%Y-%m-%dT%H:%M')
            date_time_to = datetime.datetime.strptime(f'{date}T{time_to}', '%Y-%m-%dT%H:%M')

        received_dates = DateTimeRange(f'{date}T{time_from}', f'{date}T{time_to}')

        if datetime.datetime.now() > date_time_from:
            return jsonify(message='Any booking for the past dates or time cannot be accommodated'), 406
        if date_time_from > date_time_to:
            return jsonify(message='End time must be after start time'), 406

        if datetime.datetime.strptime(date, '%Y-%m-%d').weekday() == 6:
            return jsonify(message='Sorry, appointments are only allowed from Monday to Saturday'), 406

        opening_hours = DateTimeRange(f'{date}T09:00', f'{date}T17:00')
        if not (received_dates in opening_hours):
            return jsonify(message='Appointments are only allowed from 9:00 AM - 5:00 PM'), 406

        success_message = 'You updated a record!'
        datas = Appointment.query.all()
        if datas:
            for data in datas:
                data_dates = DateTimeRange(str(data.date_time_from).replace(' ', 'T'), str(data.date_time_to).replace(' ', 'T'))
                if data_dates.is_intersection(received_dates):
                    if data.id != id:
                        return jsonify(message='There is a conflict between your schedule'), 409

        record.first_name = data['first_name']
        record.last_name = data['last_name']
        record.comments = data['comments']
        record.date_time_from = date_time_from
        record.date_time_to = date_time_to

        db.session.commit()
        return jsonify(message="You updated a record"), 202
    else:
        return jsonify(message="Record not found!"), 404

## Show Appointments
@app.route('/show_appointments', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def show_appointments():
    date_from = request.json['date_from']
    date_to = request.json['date_to']
    if not date_from:
        date_from = str(datetime.datetime.now().date())
    if not date_to:
        date_to = str(datetime.datetime.now().date())
    _date_from = datetime.datetime.strptime(f'{date_from}T09:00', '%Y-%m-%dT%H:%M')
    _date_to = datetime.datetime.strptime(f'{date_to}T17:00', '%Y-%m-%dT%H:%M')
    data = Appointment.query.filter(Appointment.date_time_from <= _date_to).filter(Appointment.date_time_from >= _date_from).order_by(Appointment.date_time_from.asc())
    result = appointments_schema.dump(data)
    result_sorted = sorted(result, key=lambda r: datetime.datetime.strptime(r["date_time_from"], "%Y-%m-%dT%H:%M:%S"))
    return jsonify(result_sorted)

## Show only one appointment
@app.route('/appointment_details/<int:appointment_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def appointment_details(appointment_id: int):
    data = Appointment.query.filter_by(id=appointment_id).first()
    if data:
        result = appointment_schema.dump(data)
        return jsonify(result), 200
    else:
        return jsonify(message='Record not found'), 404

## Delete Appointments
@app.route('/delete_appointments/<int:record_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Methods'])
def delete_appointments(record_id: int):
    data = Appointment.query.filter_by(id=record_id).first()
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify(message='You deleted a record'), 202
    else:
        return jsonify(message='That record does not exist'), 404

## Add Vehicle Booking
@app.route('/add_vehicle_booking', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def add_vehicle_booking():
    data = request.json
    date = data['date']
    time_from = data['time_from']
    time_to = data['time_to']
    vehicle_type = data['vehicle_type']

    if not date or not time_from or not time_to or not vehicle_type:
        return jsonify(message='Date, time, and vehicle type cannot be blank'), 406

    date_time_from = datetime.datetime.strptime(f'{date}-{time_from}', '%Y-%m-%d-%H:%M')
    date_time_to = datetime.datetime.strptime(f'{date}-{time_to}', '%Y-%m-%d-%H:%M')
    received_dates = DateTimeRange(f'{date}T{time_from}', f'{date}T{time_to}')

    if datetime.datetime.now() > date_time_from:
        return jsonify(message='Any booking for the past dates or time cannot be accommodated'), 406
    if date_time_from > date_time_to:
        return jsonify(message='End time must be after start time'), 406

    if datetime.datetime.strptime(date, '%Y-%m-%d').weekday() == 6:
        return jsonify(message='Sorry, bookings are only allowed from Monday to Saturday'), 406

    opening_hours = DateTimeRange(f'{date}T09:00', f'{date}T17:00')
    if not (received_dates in opening_hours):
        return jsonify(message='Bookings are only allowed from 9:00 AM - 5:00 PM'), 406

    success_message = 'You added a new vehicle booking!'
    datas = VehicleBooking.query.all()
    if datas:
        for data in datas:
            data_dates = DateTimeRange(str(data.date_time_from).replace(' ', 'T'), str(data.date_time_to).replace(' ', 'T'))
            if data_dates.is_intersection(received_dates):
                return jsonify(message='There is a conflict between your schedule'), 409

    new_vehicle_booking = VehicleBooking(
        first_name=data['first_name'],
        last_name=data['last_name'],
        vehicle_type=vehicle_type,
        date_time_from=date_time_from,
        date_time_to=date_time_to
    )

    db.session.add(new_vehicle_booking)
    db.session.commit()

    return jsonify(message=success_message), 201

## Update Vehicle Booking
@app.route('/update_vehicle_booking/<int:id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def update_vehicle_booking(id: int):
    record = VehicleBooking.query.filter_by(id=id).first()
    if record:
        data = request.json
        date = data['date']
        time_from = data['time_from']
        time_to = data['time_to']
        vehicle_type = data['vehicle_type']

        if not date or not time_from or not time_to or not vehicle_type:
            return jsonify(message='Date, time, and vehicle type cannot be blank'), 406

        try:
            date_time_from = datetime.datetime.strptime(f'{date}T{time_from}', '%Y-%m-%dT%H:%M:%S')
            date_time_to = datetime.datetime.strptime(f'{date}T{time_to}', '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            date_time_from = datetime.datetime.strptime(f'{date}T{time_from}', '%Y-%m-%dT%H:%M')
            date_time_to = datetime.datetime.strptime(f'{date}T{time_to}', '%Y-%m-%dT%H:%M')

        received_dates = DateTimeRange(f'{date}T{time_from}', f'{date}T{time_to}')

        if datetime.datetime.now() > date_time_from:
            return jsonify(message='Any booking for the past dates or time cannot be accommodated'), 406
        if date_time_from > date_time_to:
            return jsonify(message='End time must be after start time'), 406

        if datetime.datetime.strptime(date, '%Y-%m-%d').weekday() == 6:
            return jsonify(message='Sorry, bookings are only allowed from Monday to Saturday'), 406

        opening_hours = DateTimeRange(f'{date}T09:00', f'{date}T17:00')
        if not (received_dates in opening_hours):
            return jsonify(message='Bookings are only allowed from 9:00 AM - 5:00 PM'), 406

        success_message = 'You updated a vehicle booking!'
        datas = VehicleBooking.query.all()
        if datas:
            for data in datas:
                data_dates = DateTimeRange(str(data.date_time_from).replace(' ', 'T'), str(data.date_time_to).replace(' ', 'T'))
                if data_dates.is_intersection(received_dates):
                    if data.id != id:
                        return jsonify(message='There is a conflict between your schedule'), 409

        record.first_name = data['first_name']
        record.last_name = data['last_name']
        record.vehicle_type = data['vehicle_type']
        record.date_time_from = date_time_from
        record.date_time_to = date_time_to

        db.session.commit()
        return jsonify(message="You updated a vehicle booking"), 202
    else:
        return jsonify(message="Record not found!"), 404

## Show Vehicle Bookings
@app.route('/show_vehicle_bookings', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def show_vehicle_bookings():
    date_from = request.json['date_from']
    date_to = request.json['date_to']
    if not date_from:
        date_from = str(datetime.datetime.now().date())
    if not date_to:
        date_to = str(datetime.datetime.now().date())
    _date_from = datetime.datetime.strptime(f'{date_from}T09:00', '%Y-%m-%dT%H:%M')
    _date_to = datetime.datetime.strptime(f'{date_to}T17:00', '%Y-%m-%dT%H:%M')
    data = VehicleBooking.query.filter(VehicleBooking.date_time_from <= _date_to).filter(VehicleBooking.date_time_from >= _date_from).order_by(VehicleBooking.date_time_from.asc())
    result = vehicle_bookings_schema.dump(data)
    result_sorted = sorted(result, key=lambda r: datetime.datetime.strptime(r["date_time_from"], "%Y-%m-%dT%H:%M:%S"))
    return jsonify(result_sorted)

## Show only one vehicle booking
@app.route('/vehicle_booking_details/<int:vehicle_booking_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def vehicle_booking_details(vehicle_booking_id: int):
    data = VehicleBooking.query.filter_by(id=vehicle_booking_id).first()
    if data:
        result = vehicle_booking_schema.dump(data)
        return jsonify(result), 200
    else:
        return jsonify(message='Record not found'), 404

## Delete Vehicle Booking
@app.route('/delete_vehicle_booking/<int:record_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Methods'])
def delete_vehicle_booking(record_id: int):
    data = VehicleBooking.query.filter_by(id=record_id).first()
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify(message='You deleted a vehicle booking'), 202
    else:
        return jsonify(message='That record does not exist'), 404

## Running the App
if __name__ == '__main__':
    app.run(debug=True)
