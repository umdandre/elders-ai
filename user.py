from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_elder = db.Column(db.Boolean, default=True)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    caregiver = db.relationship('User', remote_side=[id], backref='elders')
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    medications = db.relationship('Medication', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'phone_number': self.phone_number,
            'emergency_contact': self.emergency_contact,
            'is_elder': self.is_elder,
            'caregiver_id': self.caregiver_id,
            'created_at': self.created_at.isoformat()
        }

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # user/ai/system
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mood_score = db.Column(db.Integer)  # 1-10 scale
    contains_concern = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message_text': self.message_text,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat(),
            'mood_score': self.mood_score,
            'contains_concern': self.contains_concern
        }

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    time_slots = db.Column(db.Text)  # JSON array of times
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    logs = db.relationship('MedicationLog', backref='medication', lazy=True)

    def get_time_slots(self):
        return json.loads(self.time_slots) if self.time_slots else []

    def set_time_slots(self, slots):
        self.time_slots = json.dumps(slots)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'medication_name': self.medication_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'time_slots': self.get_time_slots(),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active
        }

class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    taken_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)  # taken/missed/late
    confirmation_method = db.Column(db.String(20))  # voice/text/manual

    def to_dict(self):
        return {
            'id': self.id,
            'medication_id': self.medication_id,
            'user_id': self.user_id,
            'scheduled_time': self.scheduled_time.isoformat(),
            'taken_time': self.taken_time.isoformat() if self.taken_time else None,
            'status': self.status,
            'confirmation_method': self.confirmation_method
        }

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200))
    doctor_name = db.Column(db.String(100))
    appointment_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='scheduled')  # scheduled/completed/cancelled
    reminder_sent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': self.appointment_time.isoformat(),
            'location': self.location,
            'doctor_name': self.doctor_name,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'reminder_sent': self.reminder_sent
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    due_time = db.Column(db.Time)
    priority = db.Column(db.String(20), default='medium')  # low/medium/high
    status = db.Column(db.String(20), default='pending')  # pending/completed/overdue
    category = db.Column(db.String(50))  # medication/appointment/daily/health

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_description': self.task_description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'due_time': self.due_time.isoformat() if self.due_time else None,
            'priority': self.priority,
            'status': self.status,
            'category': self.category
        }

class CaregiverReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_date = db.Column(db.Date, default=datetime.utcnow().date)
    mood_summary = db.Column(db.Text)
    medication_compliance = db.Column(db.Float)  # Percentage
    appointment_attendance = db.Column(db.Float)  # Percentage
    concerns_raised = db.Column(db.Text)
    ai_insights = db.Column(db.Text)  # JSON string

    def get_ai_insights(self):
        return json.loads(self.ai_insights) if self.ai_insights else {}

    def set_ai_insights(self, insights):
        self.ai_insights = json.dumps(insights)

    def to_dict(self):
        return {
            'id': self.id,
            'elder_id': self.elder_id,
            'caregiver_id': self.caregiver_id,
            'report_date': self.report_date.isoformat(),
            'mood_summary': self.mood_summary,
            'medication_compliance': self.medication_compliance,
            'appointment_attendance': self.appointment_attendance,
            'concerns_raised': self.concerns_raised,
            'ai_insights': self.get_ai_insights()
        }

