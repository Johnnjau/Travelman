from flask import Blueprint, request, jsonify
from extensions import db
from schemas import AppointmentSchema  # Absolute import
from models import Appointment  # Import here to avoid circular imports

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    result = AppointmentSchema(many=True).dump(appointments)
    return jsonify(result)

@appointments_bp.route('/appointments/<int:record_id>', methods=['GET'])
def get_appointment(record_id: int):
    appointment = Appointment.query.get_or_404(record_id)
    result = AppointmentSchema().dump(appointment)
    return jsonify(result)

@appointments_bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    new_appointment = Appointment(
        first_name=data['first_name'],
        last_name=data['last_name'],
        comments=data.get('comments', ''),
        date_time_from=data['date_time_from'],
        date_time_to=data['date_time_to']
    )
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify(message='Appointment created'), 201

@appointments_bp.route('/appointments/<int:record_id>', methods=['PUT'])
def update_appointment(record_id: int):
    appointment = Appointment.query.get_or_404(record_id)
    data = request.get_json()
    appointment.first_name = data['first_name']
    appointment.last_name = data['last_name']
    appointment.comments = data.get('comments', '')
    appointment.date_time_from = data['date_time_from']
    appointment.date_time_to = data['date_time_to']
    db.session.commit()
    return jsonify(message='Appointment updated'), 200

@appointments_bp.route('/appointments/<int:record_id>', methods=['DELETE'])
def delete_appointment(record_id: int):
    appointment = Appointment.query.get_or_404(record_id)
    db.session.delete(appointment)
    db.session.commit()
    return jsonify(message='Appointment deleted'), 202
