from flask import Blueprint, request, jsonify
from src.models.user import db, Conversation, User
from src.routes.auth import verify_token
from datetime import datetime
import json
import random

ai_bp = Blueprint('ai', __name__)

# AI Personality and Response System
class ElderCareAI:
    def __init__(self):
        self.personality = {
            "name": "Care",
            "traits": ["warm", "patient", "understanding", "gentle", "encouraging"],
            "communication_style": "simple, clear, and caring"
        }
        
        # Conversation patterns and responses
        self.responses = {
            "greeting": [
                "Good morning! How are you feeling today?",
                "Hello there! I hope you're having a wonderful day.",
                "Hi! It's so nice to see you. How can I help you today?",
                "Good day! I'm here and ready to chat with you."
            ],
            "medication_reminder": [
                "It's time for your medication. Have you taken your pills today?",
                "Don't forget about your morning medication. Shall I remind you which ones to take?",
                "Your medication reminder is here. Would you like me to go through your list?",
                "Time for your pills! Let me know when you've taken them."
            ],
            "appointment_reminder": [
                "You have an appointment coming up. Would you like me to tell you about it?",
                "Don't forget about your doctor's appointment. Shall I help you prepare?",
                "Your appointment is scheduled soon. Would you like me to book transportation?",
                "I wanted to remind you about your upcoming medical appointment."
            ],
            "mood_check": [
                "How are you feeling emotionally today? I'm here to listen.",
                "On a scale of 1 to 10, how would you rate your mood today?",
                "I notice you might be feeling down. Would you like to talk about it?",
                "Your emotional well-being is important to me. How are you doing?"
            ],
            "emergency_response": [
                "I'm here to help! If this is a medical emergency, please call 911 immediately.",
                "I understand you need help. Should I contact your emergency contact?",
                "Let me assist you. Is this urgent? I can reach out to your caregiver.",
                "I'm concerned about you. What kind of help do you need right now?"
            ],
            "encouragement": [
                "You're doing great! I'm proud of how well you're taking care of yourself.",
                "Remember, I'm always here for you. You're not alone.",
                "You're very important to me and your family. Keep up the good work!",
                "Every day you're getting stronger. I believe in you."
            ],
            "default": [
                "I understand. Is there anything specific I can help you with today?",
                "Thank you for sharing that with me. How else can I assist you?",
                "I'm here to listen and help. What would you like to talk about?",
                "That's interesting. Tell me more about how you're feeling."
            ]
        }
        
        # Keywords for intent recognition
        self.intent_keywords = {
            "medication": ["pill", "medication", "medicine", "drug", "dose", "tablet"],
            "appointment": ["appointment", "doctor", "visit", "clinic", "hospital", "checkup"],
            "mood": ["feel", "mood", "sad", "happy", "worried", "anxious", "depressed", "lonely"],
            "emergency": ["help", "emergency", "urgent", "pain", "hurt", "sick", "call"],
            "greeting": ["hello", "hi", "good morning", "good afternoon", "good evening"],
            "gratitude": ["thank", "thanks", "appreciate", "grateful"]
        }
    
    def analyze_mood(self, message_text):
        """Analyze the mood of the user's message"""
        positive_words = ["good", "great", "happy", "wonderful", "excellent", "fine", "okay", "well"]
        negative_words = ["bad", "sad", "terrible", "awful", "sick", "pain", "hurt", "worried", "lonely"]
        
        text_lower = message_text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 8  # Good mood
        elif negative_count > positive_count:
            return 4  # Lower mood
        else:
            return 6  # Neutral mood
    
    def detect_concerns(self, message_text):
        """Detect if the message contains concerning content"""
        concern_keywords = [
            "pain", "hurt", "sick", "emergency", "help", "can't", "unable", 
            "forgot", "confused", "dizzy", "chest pain", "breathing", "fall", "fell"
        ]
        
        text_lower = message_text.lower()
        return any(keyword in text_lower for keyword in concern_keywords)
    
    def classify_intent(self, message_text):
        """Classify the intent of the user's message"""
        text_lower = message_text.lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        
        return "default"
    
    def generate_response(self, message_text, user_context=None):
        """Generate an appropriate AI response"""
        intent = self.classify_intent(message_text)
        mood_score = self.analyze_mood(message_text)
        contains_concern = self.detect_concerns(message_text)
        
        # Select appropriate response category
        if intent in self.responses:
            response_category = intent
        else:
            response_category = "default"
        
        # Add context-specific responses
        if contains_concern:
            if "emergency" in message_text.lower() or "help" in message_text.lower():
                response_category = "emergency_response"
            else:
                response_category = "mood_check"
        
        # Get base response
        base_responses = self.responses.get(response_category, self.responses["default"])
        response = random.choice(base_responses)
        
        # Add personalization if user context is available
        if user_context and user_context.get("full_name"):
            name = user_context["full_name"].split()[0]  # First name only
            if response_category == "greeting":
                response = f"Hello {name}! " + response
        
        # Add encouraging follow-up for low mood
        if mood_score <= 4:
            encouragement = random.choice(self.responses["encouragement"])
            response += f" {encouragement}"
        
        return {
            "response": response,
            "intent": intent,
            "mood_score": mood_score,
            "contains_concern": contains_concern
        }

# Initialize AI instance
elder_care_ai = ElderCareAI()

@ai_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        
        # Generate AI response
        ai_result = elder_care_ai.generate_response(
            user_message, 
            user_context=user.to_dict()
        )
        
        # Save user message to database
        user_conversation = Conversation(
            user_id=user.id,
            message_text=user_message,
            message_type='user',
            mood_score=ai_result['mood_score'],
            contains_concern=ai_result['contains_concern']
        )
        db.session.add(user_conversation)
        
        # Save AI response to database
        ai_conversation = Conversation(
            user_id=user.id,
            message_text=ai_result['response'],
            message_type='ai',
            mood_score=ai_result['mood_score'],
            contains_concern=ai_result['contains_concern']
        )
        db.session.add(ai_conversation)
        
        db.session.commit()
        
        return jsonify({
            'response': ai_result['response'],
            'intent': ai_result['intent'],
            'mood_score': ai_result['mood_score'],
            'contains_concern': ai_result['contains_concern'],
            'conversation_id': ai_conversation.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai/mood-analysis/<int:user_id>', methods=['GET'])
def get_mood_analysis(user_id):
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
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get conversations with mood scores
        conversations = Conversation.query.filter(
            Conversation.user_id == user_id,
            Conversation.timestamp >= start_date,
            Conversation.timestamp <= end_date,
            Conversation.mood_score.isnot(None)
        ).order_by(Conversation.timestamp).all()
        
        if not conversations:
            return jsonify({
                'mood_analysis': {
                    'average_mood': None,
                    'mood_trend': 'stable',
                    'total_conversations': 0,
                    'concerns_count': 0
                }
            }), 200
        
        # Calculate mood statistics
        mood_scores = [conv.mood_score for conv in conversations]
        average_mood = sum(mood_scores) / len(mood_scores)
        
        # Calculate trend (simple: compare first half vs second half)
        mid_point = len(mood_scores) // 2
        if mid_point > 0:
            first_half_avg = sum(mood_scores[:mid_point]) / mid_point
            second_half_avg = sum(mood_scores[mid_point:]) / (len(mood_scores) - mid_point)
            
            if second_half_avg > first_half_avg + 0.5:
                trend = 'improving'
            elif second_half_avg < first_half_avg - 0.5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Count concerns
        concerns_count = len([conv for conv in conversations if conv.contains_concern])
        
        return jsonify({
            'mood_analysis': {
                'average_mood': round(average_mood, 1),
                'mood_trend': trend,
                'total_conversations': len(conversations),
                'concerns_count': concerns_count,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai/proactive-check', methods=['POST'])
def proactive_check():
    """Generate proactive check-in messages for users"""
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Generate a proactive check-in message
        check_in_messages = [
            "Good morning! How are you feeling today? I'm here if you need anything.",
            "I hope you're having a good day! Don't forget to take your medications if you haven't already.",
            "Just checking in on you. How has your day been so far?",
            "I wanted to see how you're doing. Is there anything I can help you with today?",
            "Good afternoon! Have you been staying hydrated and taking care of yourself?"
        ]
        
        message = random.choice(check_in_messages)
        
        # Save proactive message to database
        proactive_conversation = Conversation(
            user_id=user.id,
            message_text=message,
            message_type='ai'
        )
        db.session.add(proactive_conversation)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'conversation_id': proactive_conversation.id,
            'type': 'proactive_check'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/ai/transcribe', methods=['POST'])
def transcribe_audio():
    """Simulate voice-to-text transcription"""
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # In a real implementation, this would process audio data
        # For now, we'll simulate transcription
        data = request.get_json()
        duration = data.get('duration', 5)  # seconds
        
        # Simulate transcription based on duration
        if duration < 3:
            transcription = "Hello"
        elif duration < 10:
            transcription = "I need help with my medications"
        else:
            transcription = "I'm feeling a bit lonely today and was wondering if we could chat for a while"
        
        return jsonify({
            'transcription': transcription,
            'confidence': 0.95,
            'duration': duration
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

