from flask import Blueprint, request, jsonify
from src.models.user import db, Medication, MedicationLog
from src.routes.auth import verify_token
from datetime import datetime, date, timedelta

medications_bp = Blueprint('medications', __name__)

@medications_bp.route('/medications/<int:user_id>', methods=['GET'])
def get_medications(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access these medications
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        medications = Medication.query.filter_by(user_id=user_id, is_active=True).all()
        
        return jsonify({
            'medications': [med.to_dict() for med in medications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medications_bp.route('/medications', methods=['POST'])
def create_medication():
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['medication_name', 'dosage', 'frequency', 'start_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        medication = Medication(
            user_id=data.get('user_id', user.id),
            medication_name=data['medication_name'],
            dosage=data['dosage'],
            frequency=data['frequency'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        )
        
        if 'end_date' in data:
            medication.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'time_slots' in data:
            medication.set_time_slots(data['time_slots'])
        
        db.session.add(medication)
        db.session.commit()
        
        return jsonify({
            'message': 'Medication created successfully',
            'medication': medication.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medications_bp.route('/medications/<int:medication_id>', methods=['PUT'])
def update_medication(medication_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        medication = Medication.query.get(medication_id)
        if not medication:
            return jsonify({'error': 'Medication not found'}), 404
        
        # Check if user can update this medication
        if user.id != medication.user_id and user.caregiver_id != medication.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'medication_name' in data:
            medication.medication_name = data['medication_name']
        if 'dosage' in data:
            medication.dosage = data['dosage']
        if 'frequency' in data:
            medication.frequency = data['frequency']
        if 'time_slots' in data:
            medication.set_time_slots(data['time_slots'])
        if 'end_date' in data:
            medication.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'is_active' in data:
            medication.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Medication updated successfully',
            'medication': medication.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medications_bp.route('/medications/<int:medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        medication = Medication.query.get(medication_id)
        if not medication:
            return jsonify({'error': 'Medication not found'}), 404
        
        # Check if user can delete this medication
        if user.id != medication.user_id and user.caregiver_id != medication.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Soft delete by setting is_active to False
        medication.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Medication deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medications_bp.route('/medications/<int:medication_id>/log', methods=['POST'])
def log_medication(medication_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        medication = Medication.query.get(medication_id)
        if not medication:
            return jsonify({'error': 'Medication not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if 'status' not in data:
            return jsonify({'error': 'status is required'}), 400
        
        log = MedicationLog(
            medication_id=medication_id,
            user_id=medication.user_id,
            scheduled_time=datetime.fromisoformat(data['scheduled_time']) if 'scheduled_time' in data else datetime.utcnow(),
            taken_time=datetime.utcnow() if data['status'] == 'taken' else None,
            status=data['status'],
            confirmation_method=data.get('confirmation_method', 'manual')
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Medication log created successfully',
            'log': log.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medications_bp.route('/medications/<int:user_id>/compliance', methods=['GET'])
def get_medication_compliance(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access this data
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get date range
        days = request.args.get('days', 7, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        logs = MedicationLog.query.filter(
            MedicationLog.user_id == user_id,
            MedicationLog.scheduled_time >= start_date,
            MedicationLog.scheduled_time <= end_date
        ).all()
        
        total_scheduled = len(logs)
        taken = len([log for log in logs if log.status == 'taken'])
        compliance_rate = (taken / total_scheduled * 100) if total_scheduled > 0 else 0
        
        return jsonify({
            'compliance': {
                'total_scheduled': total_scheduled,
                'taken': taken,
                'missed': total_scheduled - taken,
                'compliance_rate': round(compliance_rate, 2),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

