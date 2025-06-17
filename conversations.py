from flask import Blueprint, request, jsonify
from src.models.user import db, Conversation
from src.routes.auth import verify_token
from datetime import datetime, timedelta

conversations_bp = Blueprint('conversations', __name__)

@conversations_bp.route('/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access these conversations
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        conversations = Conversation.query.filter_by(user_id=user_id)\
            .order_by(Conversation.timestamp.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations],
            'total': Conversation.query.filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations', methods=['POST'])
def create_conversation():
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if 'message_text' not in data or 'message_type' not in data:
            return jsonify({'error': 'message_text and message_type are required'}), 400
        
        conversation = Conversation(
            user_id=data.get('user_id', user.id),
            message_text=data['message_text'],
            message_type=data['message_type'],
            mood_score=data.get('mood_score'),
            contains_concern=data.get('contains_concern', False)
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'message': 'Conversation saved successfully',
            'conversation': conversation.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations/<int:user_id>/summary', methods=['GET'])
def get_conversation_summary(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access these conversations
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get date range
        days = request.args.get('days', 7, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        conversations = Conversation.query.filter(
            Conversation.user_id == user_id,
            Conversation.timestamp >= start_date,
            Conversation.timestamp <= end_date
        ).all()
        
        # Calculate summary statistics
        total_messages = len(conversations)
        ai_messages = len([c for c in conversations if c.message_type == 'ai'])
        user_messages = len([c for c in conversations if c.message_type == 'user'])
        concerns = len([c for c in conversations if c.contains_concern])
        
        mood_scores = [c.mood_score for c in conversations if c.mood_score]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else None
        
        return jsonify({
            'summary': {
                'total_messages': total_messages,
                'ai_messages': ai_messages,
                'user_messages': user_messages,
                'concerns_raised': concerns,
                'average_mood': avg_mood,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

