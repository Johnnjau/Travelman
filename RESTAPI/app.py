from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, desc, asc
from flask_marshmallow import Marshmallow
import datetime
from datetimerange import DateTimeRange
from flask_cors import CORS, cross_origin
import os

# Setting up the app
app = Flask(__name__)
CORS(app)

# Setting up SQLAlchemy
basedir = os.getcwd()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(basedir, 'booking.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Adding CLI Command for DB creation and deletion
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

# Creating API

# Utility function to parse datetime
def parse_datetime(date, time):
    try:
        return datetime.datetime.strptime(f'{date}T{time}', '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return datetime.datetime.strptime(f'{date}T{time}', '%Y-%m-%dT%H:%M')

# Default Route
@app.route('/')
def home():
    return jsonify(message='Booking API')

# Add Appointments
@app.route('/add_appointments', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def add_appointment():
    data = request.json
    try:
        date = data['date']
        time_from = data['time_from']
        time_to = data['time_to']
        first_name = data['first_name']
        last_name = data['last_name']
        comments = data.get('comments', '')  # Optional field
    except KeyError as e:
        return jsonify(message=f"Missing key: {e.args[0]}"), 400

    date_time_from = parse_datetime(date, time_from)
    date_time_to = parse_datetime(date, time_to)
    received_dates = DateTimeRange(f'{date}T{time_from}', f'{date}T{time_to}')

    # Validate date and time
    if datetime.datetime.now() > date_time_from:
        return jsonify(message='Bookings for past dates or times are not allowed'), 406
    if date_time_from > date_time_to:
        return jsonify(message='End time cannot be before start time'), 406

    # Booking not allowed on Sunday
    if date_time_from.weekday() == 6:
        return jsonify(message='Sorry, appointments are only allowed from Monday to Saturday'), 406

    # Bookings only allowed during opening hours
    opening_hours = DateTimeRange(f'{date}T09:00', f'{date}T17:00')
    if not (received_dates in opening_hours):
        return jsonify(message='Appointments are only allowed from 9:00AM - 5:00PM'), 406

    # Check for conflicting bookings
    existing_appointments = Appointment.query.all()
    for appointment in existing_appointments:
        existing_dates = DateTimeRange(str(appointment.date_time_from).replace(' ', 'T'),
                                       str(appointment.date_time_to).replace(' ', 'T'))
        if existing_dates.is_intersection(received_dates):
            return jsonify(message='There is a conflict with an existing appointment'), 409

    # Add new appointment to the database
    new_appointment = Appointment(
        first_name=first_name,
        last_name=last_name,
        comments=comments,
        date_time_from=date_time_from,
        date_time_to=date_time_to
    )

    try:
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify(message='New appointment added successfully'), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(message='An error occurred while adding the appointment', error=str(e)), 500

# ... (Remaining routes stay largely the same)

if __name__ == '__main__':
    app.run()
