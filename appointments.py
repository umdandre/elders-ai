from flask import Blueprint, request, jsonify
from src.models.user import db, Appointment
from src.routes.auth import verify_token
from datetime import datetime, date, timedelta

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments/<int:user_id>', methods=['GET'])
def get_appointments(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access these appointments
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        upcoming_only = request.args.get('upcoming', 'false').lower() == 'true'
        
        query = Appointment.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if upcoming_only:
            query = query.filter(Appointment.appointment_date >= date.today())
        
        appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        return jsonify({
            'appointments': [apt.to_dict() for apt in appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/appointments', methods=['POST'])
def create_appointment():
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        appointment = Appointment(
            user_id=data.get('user_id', user.id),
            title=data['title'],
            description=data.get('description'),
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(data['appointment_time'], '%H:%M').time(),
            location=data.get('location'),
            doctor_name=data.get('doctor_name'),
            appointment_type=data.get('appointment_type')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Check if user can update this appointment
        if user.id != appointment.user_id and user.caregiver_id != appointment.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            appointment.title = data['title']
        if 'description' in data:
            appointment.description = data['description']
        if 'appointment_date' in data:
            appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        if 'appointment_time' in data:
            appointment.appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        if 'location' in data:
            appointment.location = data['location']
        if 'doctor_name' in data:
            appointment.doctor_name = data['doctor_name']
        if 'appointment_type' in data:
            appointment.appointment_type = data['appointment_type']
        if 'status' in data:
            appointment.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Check if user can delete this appointment
        if user.id != appointment.user_id and user.caregiver_id != appointment.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(appointment)
        db.session.commit()
        
        return jsonify({'message': 'Appointment deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/appointments/<int:user_id>/upcoming', methods=['GET'])
def get_upcoming_appointments(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access these appointments
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get appointments for the next 30 days
        end_date = date.today() + timedelta(days=30)
        
        appointments = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.appointment_date >= date.today(),
            Appointment.appointment_date <= end_date,
            Appointment.status == 'scheduled'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        return jsonify({
            'upcoming_appointments': [apt.to_dict() for apt in appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

