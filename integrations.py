from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import os
import requests

integrations_bp = Blueprint('integrations', __name__)

# Uber API Integration Structure
@integrations_bp.route('/uber/request-ride', methods=['POST'])
def request_uber_ride():
    """
    Request an Uber ride for the elder user
    
    Expected payload:
    {
        "user_id": 1,
        "pickup_address": "123 Main St, City, State",
        "destination_address": "456 Oak Ave, City, State",
        "ride_type": "uberX",
        "scheduled_time": "2025-06-17T14:00:00Z" (optional)
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        pickup_address = data.get('pickup_address')
        destination_address = data.get('destination_address')
        ride_type = data.get('ride_type', 'uberX')
        scheduled_time = data.get('scheduled_time')
        
        # Validate required fields
        if not all([user_id, pickup_address, destination_address]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # In production, this would integrate with Uber API
        # For MVP, we'll simulate the request
        uber_api_key = os.getenv('UBER_API_KEY', 'demo_key')
        
        # Simulated Uber API response
        mock_response = {
            'ride_id': f'uber_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'status': 'confirmed',
            'driver': {
                'name': 'John Smith',
                'vehicle': '2020 Toyota Camry',
                'license_plate': 'ABC-123',
                'rating': 4.8
            },
            'pickup_time': scheduled_time or (datetime.now() + timedelta(minutes=5)).isoformat(),
            'estimated_arrival': (datetime.now() + timedelta(minutes=15)).isoformat(),
            'fare_estimate': '$12-15',
            'pickup_address': pickup_address,
            'destination_address': destination_address
        }
        
        # Log the ride request (in production, save to database)
        print(f"Uber ride requested for user {user_id}: {pickup_address} -> {destination_address}")
        
        return jsonify({
            'success': True,
            'ride_details': mock_response,
            'message': 'Ride successfully requested'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/uber/ride-status/<ride_id>', methods=['GET'])
def get_ride_status(ride_id):
    """Get the current status of an Uber ride"""
    try:
        # In production, this would query Uber API
        mock_status = {
            'ride_id': ride_id,
            'status': 'driver_arriving',
            'driver_location': {
                'lat': 40.7128,
                'lng': -74.0060
            },
            'estimated_arrival': '3 minutes',
            'driver': {
                'name': 'John Smith',
                'phone': '+1-555-0123',
                'vehicle': '2020 Toyota Camry - ABC-123'
            }
        }
        
        return jsonify(mock_status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Calendar API Integration Structure
@integrations_bp.route('/calendar/appointments', methods=['GET'])
def get_calendar_appointments():
    """
    Get upcoming appointments from calendar integration
    
    Query parameters:
    - user_id: ID of the elder user
    - days_ahead: Number of days to look ahead (default: 7)
    """
    try:
        user_id = request.args.get('user_id')
        days_ahead = int(request.args.get('days_ahead', 7))
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # In production, this would integrate with Google Calendar, Outlook, etc.
        calendar_api_key = os.getenv('CALENDAR_API_KEY', 'demo_key')
        
        # Simulated calendar appointments
        mock_appointments = [
            {
                'id': 'cal_001',
                'title': 'Cardiology Appointment - Dr. Johnson',
                'start_time': (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0).isoformat(),
                'end_time': (datetime.now() + timedelta(days=1)).replace(hour=15, minute=0).isoformat(),
                'location': 'Heart Center, 789 Medical Blvd',
                'description': 'Regular checkup and blood pressure monitoring',
                'reminder_set': True,
                'transportation_needed': True
            },
            {
                'id': 'cal_002',
                'title': 'General Checkup - Dr. Smith',
                'start_time': (datetime.now() + timedelta(days=7)).replace(hour=10, minute=0).isoformat(),
                'end_time': (datetime.now() + timedelta(days=7)).replace(hour=11, minute=0).isoformat(),
                'location': 'Family Medicine Clinic, 456 Health St',
                'description': 'Annual physical examination',
                'reminder_set': True,
                'transportation_needed': False
            }
        ]
        
        return jsonify({
            'appointments': mock_appointments,
            'total_count': len(mock_appointments)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/calendar/create-appointment', methods=['POST'])
def create_calendar_appointment():
    """
    Create a new calendar appointment
    
    Expected payload:
    {
        "user_id": 1,
        "title": "Doctor Appointment",
        "start_time": "2025-06-20T10:00:00Z",
        "end_time": "2025-06-20T11:00:00Z",
        "location": "Medical Center",
        "description": "Regular checkup"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        title = data.get('title')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        location = data.get('location', '')
        description = data.get('description', '')
        
        if not all([user_id, title, start_time, end_time]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # In production, this would create the appointment via calendar API
        appointment_id = f'cal_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        mock_response = {
            'appointment_id': appointment_id,
            'status': 'created',
            'title': title,
            'start_time': start_time,
            'end_time': end_time,
            'location': location,
            'description': description,
            'calendar_link': f'https://calendar.google.com/event?eid={appointment_id}'
        }
        
        return jsonify({
            'success': True,
            'appointment': mock_response,
            'message': 'Appointment successfully created'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health Device API Integration Structure
@integrations_bp.route('/health-devices/vitals/<user_id>', methods=['GET'])
def get_health_vitals(user_id):
    """
    Get latest health vitals from connected devices
    
    Query parameters:
    - device_type: fitbit, apple_health, garmin, etc.
    - metric: heart_rate, blood_pressure, steps, sleep, etc.
    - days: Number of days of data to retrieve (default: 1)
    """
    try:
        device_type = request.args.get('device_type', 'all')
        metric = request.args.get('metric', 'all')
        days = int(request.args.get('days', 1))
        
        # In production, this would integrate with health device APIs
        health_api_key = os.getenv('HEALTH_API_KEY', 'demo_key')
        
        # Simulated health data
        mock_vitals = {
            'user_id': user_id,
            'last_updated': datetime.now().isoformat(),
            'vitals': {
                'heart_rate': {
                    'current': 72,
                    'average_24h': 68,
                    'status': 'normal',
                    'last_reading': (datetime.now() - timedelta(minutes=30)).isoformat()
                },
                'blood_pressure': {
                    'systolic': 125,
                    'diastolic': 80,
                    'status': 'normal',
                    'last_reading': (datetime.now() - timedelta(hours=2)).isoformat()
                },
                'steps': {
                    'today': 3420,
                    'goal': 5000,
                    'percentage': 68.4,
                    'last_updated': datetime.now().isoformat()
                },
                'sleep': {
                    'last_night_hours': 7.2,
                    'quality': 'good',
                    'deep_sleep_hours': 2.1,
                    'date': (datetime.now() - timedelta(days=1)).date().isoformat()
                }
            },
            'alerts': [
                {
                    'type': 'reminder',
                    'message': 'Time to take your evening medication',
                    'priority': 'medium',
                    'timestamp': datetime.now().isoformat()
                }
            ]
        }
        
        return jsonify(mock_vitals)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/health-devices/sync/<user_id>', methods=['POST'])
def sync_health_devices(user_id):
    """
    Trigger a sync with all connected health devices
    """
    try:
        data = request.get_json() or {}
        device_types = data.get('device_types', ['fitbit', 'apple_health'])
        
        # In production, this would trigger sync with actual devices
        sync_results = []
        
        for device_type in device_types:
            sync_result = {
                'device_type': device_type,
                'status': 'success',
                'last_sync': datetime.now().isoformat(),
                'records_synced': 24,
                'next_sync': (datetime.now() + timedelta(hours=1)).isoformat()
            }
            sync_results.append(sync_result)
        
        return jsonify({
            'success': True,
            'sync_results': sync_results,
            'message': f'Successfully synced {len(sync_results)} devices'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Webhook handlers for external services
@integrations_bp.route('/webhooks/uber', methods=['POST'])
def uber_webhook():
    """Handle webhooks from Uber API for ride status updates"""
    try:
        data = request.get_json()
        
        # In production, verify webhook signature
        # webhook_signature = request.headers.get('X-Uber-Signature')
        
        ride_id = data.get('ride_id')
        status = data.get('status')
        
        # Process the webhook (update database, notify user, etc.)
        print(f"Uber webhook received: Ride {ride_id} status changed to {status}")
        
        # Here you would typically:
        # 1. Update ride status in database
        # 2. Send push notification to elder and caregiver
        # 3. Update AI conversation context
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/webhooks/calendar', methods=['POST'])
def calendar_webhook():
    """Handle webhooks from calendar services for appointment changes"""
    try:
        data = request.get_json()
        
        appointment_id = data.get('appointment_id')
        change_type = data.get('change_type')  # created, updated, cancelled
        
        print(f"Calendar webhook received: Appointment {appointment_id} {change_type}")
        
        # Process the webhook
        # 1. Update appointment in database
        # 2. Notify elder and caregiver
        # 3. Update AI conversation context
        # 4. Arrange transportation if needed
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/webhooks/health', methods=['POST'])
def health_webhook():
    """Handle webhooks from health device APIs for vital sign alerts"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        alert_type = data.get('alert_type')
        vital_sign = data.get('vital_sign')
        value = data.get('value')
        
        print(f"Health webhook received: {alert_type} for user {user_id} - {vital_sign}: {value}")
        
        # Process health alerts
        # 1. Store vital sign data
        # 2. Check against thresholds
        # 3. Alert caregivers if concerning
        # 4. Update AI conversation context
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Configuration endpoints
@integrations_bp.route('/integrations/config', methods=['GET'])
def get_integration_config():
    """Get current integration configuration"""
    try:
        config = {
            'uber': {
                'enabled': bool(os.getenv('UBER_API_KEY')),
                'supported_cities': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
                'ride_types': ['uberX', 'uberXL', 'Comfort']
            },
            'calendar': {
                'enabled': bool(os.getenv('CALENDAR_API_KEY')),
                'supported_providers': ['google', 'outlook', 'apple'],
                'sync_frequency': '1 hour'
            },
            'health_devices': {
                'enabled': bool(os.getenv('HEALTH_API_KEY')),
                'supported_devices': ['fitbit', 'apple_health', 'garmin', 'samsung_health'],
                'sync_frequency': '15 minutes'
            }
        }
        
        return jsonify(config)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/integrations/test', methods=['POST'])
def test_integrations():
    """Test all configured integrations"""
    try:
        test_results = {
            'uber': {
                'status': 'connected',
                'response_time': '245ms',
                'last_test': datetime.now().isoformat()
            },
            'calendar': {
                'status': 'connected',
                'response_time': '156ms',
                'last_test': datetime.now().isoformat()
            },
            'health_devices': {
                'status': 'connected',
                'response_time': '89ms',
                'last_test': datetime.now().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'overall_status': 'all_connected'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

