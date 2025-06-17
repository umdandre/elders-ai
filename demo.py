from flask import Blueprint, request, jsonify
from src.models.user import db, User
from datetime import datetime

# Create a test user for demo purposes
def create_demo_user():
    # Check if demo user already exists
    existing_user = User.query.filter_by(email='mary@example.com').first()
    if existing_user:
        return existing_user
    
    # Create demo user
    demo_user = User(
        email='mary@example.com',
        full_name='Mary Johnson',
        phone_number='555-0123',
        emergency_contact='Sarah Johnson (daughter) - 555-0124',
        is_elder=True
    )
    demo_user.set_password('password123')
    
    db.session.add(demo_user)
    db.session.commit()
    return demo_user

demo_bp = Blueprint('demo', __name__)

@demo_bp.route('/demo/setup', methods=['POST'])
def setup_demo():
    try:
        user = create_demo_user()
        return jsonify({
            'message': 'Demo user created successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

