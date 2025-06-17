from flask import Blueprint, request, jsonify
from src.models.user import db, User, CaregiverReport, Conversation, MedicationLog, Appointment
from src.routes.auth import verify_token
from datetime import datetime, date, timedelta

caregiver_bp = Blueprint('caregiver', __name__)

@caregiver_bp.route('/caregiver/<int:caregiver_id>/elders', methods=['GET'])
def get_caregiver_elders(caregiver_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user is the caregiver
        if user.id != caregiver_id:
            return jsonify({'error': 'Access denied'}), 403
        
        elders = User.query.filter_by(caregiver_id=caregiver_id, is_elder=True).all()
        
        return jsonify({
            'elders': [elder.to_dict() for elder in elders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@caregiver_bp.route('/caregiver/<int:elder_id>/reports', methods=['GET'])
def get_elder_reports(elder_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        elder = User.query.get(elder_id)
        if not elder:
            return jsonify({'error': 'Elder not found'}), 404
        
        # Check if user is the caregiver for this elder
        if user.id != elder.caregiver_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get date range
        days = request.args.get('days', 30, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        reports = CaregiverReport.query.filter(
            CaregiverReport.elder_id == elder_id,
            CaregiverReport.report_date >= start_date,
            CaregiverReport.report_date <= end_date
        ).order_by(CaregiverReport.report_date.desc()).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@caregiver_bp.route('/caregiver/<int:elder_id>/dashboard', methods=['GET'])
def get_elder_dashboard(elder_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        elder = User.query.get(elder_id)
        if not elder:
            return jsonify({'error': 'Elder not found'}), 404
        
        # Check if user is the caregiver for this elder
        if user.id != elder.caregiver_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get today's data
        today = date.today()
        
        # Recent conversations (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_conversations = Conversation.query.filter(
            Conversation.user_id == elder_id,
            Conversation.timestamp >= yesterday
        ).order_by(Conversation.timestamp.desc()).limit(10).all()
        
        # Medication compliance (last 7 days)
        week_ago = today - timedelta(days=7)
        medication_logs = MedicationLog.query.filter(
            MedicationLog.user_id == elder_id,
            MedicationLog.scheduled_time >= week_ago
        ).all()
        
        total_scheduled = len(medication_logs)
        taken = len([log for log in medication_logs if log.status == 'taken'])
        compliance_rate = (taken / total_scheduled * 100) if total_scheduled > 0 else 0
        
        # Mood analysis (last 7 days)
        mood_conversations = Conversation.query.filter(
            Conversation.user_id == elder_id,
            Conversation.timestamp >= yesterday,
            Conversation.mood_score.isnot(None)
        ).all()
        
        mood_scores = [c.mood_score for c in mood_conversations]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else None
        
        # Concerns raised (last 7 days)
        concerns = Conversation.query.filter(
            Conversation.user_id == elder_id,
            Conversation.timestamp >= yesterday,
            Conversation.contains_concern == True
        ).count()
        
        # Upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.user_id == elder_id,
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
        
        return jsonify({
            'dashboard': {
                'elder_info': elder.to_dict(),
                'today_interactions': len(recent_conversations),
                'medication_compliance': round(compliance_rate, 2),
                'average_mood': round(avg_mood, 1) if avg_mood else None,
                'concerns_raised': concerns,
                'recent_conversations': [conv.to_dict() for conv in recent_conversations],
                'upcoming_appointments': [apt.to_dict() for apt in upcoming_appointments]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@caregiver_bp.route('/caregiver/<int:elder_id>/alerts', methods=['GET'])
def get_elder_alerts(elder_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        elder = User.query.get(elder_id)
        if not elder:
            return jsonify({'error': 'Elder not found'}), 404
        
        # Check if user is the caregiver for this elder
        if user.id != elder.caregiver_id:
            return jsonify({'error': 'Access denied'}), 403
        
        alerts = []
        today = date.today()
        yesterday = datetime.now() - timedelta(days=1)
        
        # Check for missed medications
        missed_meds = MedicationLog.query.filter(
            MedicationLog.user_id == elder_id,
            MedicationLog.scheduled_time >= yesterday,
            MedicationLog.status == 'missed'
        ).count()
        
        if missed_meds > 0:
            alerts.append({
                'type': 'medication',
                'severity': 'high' if missed_meds > 2 else 'medium',
                'message': f'{missed_meds} missed medication(s) in the last 24 hours',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for concerning conversations
        concerning_conversations = Conversation.query.filter(
            Conversation.user_id == elder_id,
            Conversation.timestamp >= yesterday,
            Conversation.contains_concern == True
        ).all()
        
        for conv in concerning_conversations:
            alerts.append({
                'type': 'conversation',
                'severity': 'medium',
                'message': f'Concerning conversation detected: {conv.message_text[:100]}...',
                'timestamp': conv.timestamp.isoformat()
            })
        
        # Check for low mood
        low_mood_conversations = Conversation.query.filter(
            Conversation.user_id == elder_id,
            Conversation.timestamp >= yesterday,
            Conversation.mood_score <= 4
        ).all()
        
        if low_mood_conversations:
            alerts.append({
                'type': 'mood',
                'severity': 'medium',
                'message': f'Low mood detected in recent conversations',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for upcoming appointments without reminders
        upcoming_no_reminder = Appointment.query.filter(
            Appointment.user_id == elder_id,
            Appointment.appointment_date == today + timedelta(days=1),
            Appointment.reminder_sent == False
        ).all()
        
        for apt in upcoming_no_reminder:
            alerts.append({
                'type': 'appointment',
                'severity': 'low',
                'message': f'Reminder needed for appointment: {apt.title}',
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'alerts': sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@caregiver_bp.route('/caregiver/reports', methods=['POST'])
def create_caregiver_report():
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if 'elder_id' not in data:
            return jsonify({'error': 'elder_id is required'}), 400
        
        elder = User.query.get(data['elder_id'])
        if not elder:
            return jsonify({'error': 'Elder not found'}), 404
        
        # Check if user is the caregiver for this elder
        if user.id != elder.caregiver_id:
            return jsonify({'error': 'Access denied'}), 403
        
        report = CaregiverReport(
            elder_id=data['elder_id'],
            caregiver_id=user.id,
            mood_summary=data.get('mood_summary'),
            medication_compliance=data.get('medication_compliance'),
            appointment_attendance=data.get('appointment_attendance'),
            concerns_raised=data.get('concerns_raised')
        )
        
        if 'ai_insights' in data:
            report.set_ai_insights(data['ai_insights'])
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Caregiver report created successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

