from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class VehicleBooking(db.Model):
    __tablename__ = 'vehicle_bookings'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_registration_number = db.Column(db.String(20), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, date, time_from, time_to, first_name, last_name, vehicle_type, vehicle_registration_number, comments=None):
        self.date = date
        self.time_from = time_from
        self.time_to = time_to
        self.first_name = first_name
        self.last_name = last_name
        self.vehicle_type = vehicle_type
        self.vehicle_registration_number = vehicle_registration_number
        self.comments = comments
