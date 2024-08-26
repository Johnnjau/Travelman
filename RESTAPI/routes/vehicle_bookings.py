from flask import Blueprint, request, jsonify
from extensions import db
from schemas import VehicleBookingSchema  # Absolute import
from models import VehicleBooking

vehicle_bookings_bp = Blueprint('vehicle_bookings', __name__)

@vehicle_bookings_bp.route('/vehicle_bookings', methods=['GET'])
def get_vehicle_bookings():
    vehicle_bookings = VehicleBooking.query.all()
    result = VehicleBookingSchema(many=True).dump(vehicle_bookings)
    return jsonify(result)

@vehicle_bookings_bp.route('/vehicle_bookings/<int:record_id>', methods=['GET'])
def get_vehicle_booking(record_id: int):
    vehicle_booking = VehicleBooking.query.get_or_404(record_id)
    result = VehicleBookingSchema().dump(vehicle_booking)
    return jsonify(result)

@vehicle_bookings_bp.route('/vehicle_bookings', methods=['POST'])
def create_vehicle_booking():
    data = request.get_json()
    new_vehicle_booking = VehicleBooking(
        date=datetime.fromisoformat(data['date']),
        time_from=datetime.strptime(data['time_from'], '%H:%M:%S').time(),
        time_to=datetime.strptime(data['time_to'], '%H:%M:%S').time(),
        first_name=data['first_name'],
        last_name=data['last_name'],
        vehicle_type=data['vehicle_type'],
        vehicle_registration_number=data.get('vehicle_registration_number', ''),
        comments=data.get('comments', None)
    )
    db.session.add(new_vehicle_booking)
    db.session.commit()
    return jsonify(message='Vehicle booking created'), 201

@vehicle_bookings_bp.route('/vehicle_bookings/<int:record_id>', methods=['PUT'])
def update_vehicle_booking(record_id: int):
    vehicle_booking = VehicleBooking.query.get_or_404(record_id)
    data = request.get_json()
    vehicle_booking.first_name = data['first_name']
    vehicle_booking.last_name = data['last_name']
    vehicle_booking.vehicle_type = data['vehicle_type']
    vehicle_booking.date_time_from = data['date_time_from']
    vehicle_booking.date_time_to = data['date_time_to']
    db.session.commit()
    return jsonify(message='Vehicle booking updated'), 200

@vehicle_bookings_bp.route('/vehicle_bookings/<int:record_id>', methods=['DELETE'])
def delete_vehicle_booking(record_id: int):
    vehicle_booking = VehicleBooking.query.get_or_404(record_id)
    db.session.delete(vehicle_booking)
    db.session.commit()
    return jsonify(message='Vehicle booking deleted'), 202
