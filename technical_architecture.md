# Elder Care AI App MVP - Technical Architecture

## Technology Stack

### Frontend (Mobile-First Web App)
- **Framework**: React with responsive design
- **UI Library**: Material-UI with custom elderly-friendly components
- **State Management**: React Context API
- **Real-time Communication**: WebSocket/Socket.io
- **Voice Integration**: Web Speech API
- **PWA Features**: Service Workers for offline capability

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite for MVP (easily upgradeable to PostgreSQL)
- **Authentication**: JWT tokens
- **Real-time**: Flask-SocketIO
- **AI Integration**: OpenAI API or similar
- **File Storage**: Local filesystem (upgradeable to cloud storage)

### Third-Party Integrations
- **Transportation**: Uber API
- **Calendar**: Google Calendar API
- **Health Devices**: Generic REST API framework
- **Voice Services**: Web Speech API + backend transcription

## Database Schema

### Users Table
- id (Primary Key)
- email
- password_hash
- full_name
- date_of_birth
- phone_number
- emergency_contact
- created_at
- updated_at
- is_elder (boolean)
- caregiver_id (Foreign Key to Users)

### Conversations Table
- id (Primary Key)
- user_id (Foreign Key)
- message_text
- message_type (user/ai/system)
- timestamp
- mood_score (1-10)
- contains_concern (boolean)

### Medications Table
- id (Primary Key)
- user_id (Foreign Key)
- medication_name
- dosage
- frequency
- time_slots (JSON array)
- start_date
- end_date
- is_active

### Medication_Logs Table
- id (Primary Key)
- medication_id (Foreign Key)
- user_id (Foreign Key)
- scheduled_time
- taken_time
- status (taken/missed/late)
- confirmation_method (voice/text/manual)

### Appointments Table
- id (Primary Key)
- user_id (Foreign Key)
- title
- description
- appointment_date
- appointment_time
- location
- doctor_name
- appointment_type
- status (scheduled/completed/cancelled)
- reminder_sent

### Tasks Table
- id (Primary Key)
- user_id (Foreign Key)
- task_description
- due_date
- due_time
- priority (low/medium/high)
- status (pending/completed/overdue)
- category (medication/appointment/daily/health)

### Caregiver_Reports Table
- id (Primary Key)
- elder_id (Foreign Key to Users)
- caregiver_id (Foreign Key to Users)
- report_date
- mood_summary
- medication_compliance
- appointment_attendance
- concerns_raised
- ai_insights (JSON)

## API Endpoints Structure

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/profile

### Conversations
- GET /api/conversations/{user_id}
- POST /api/conversations
- GET /api/conversations/{user_id}/summary

### Medications
- GET /api/medications/{user_id}
- POST /api/medications
- PUT /api/medications/{id}
- DELETE /api/medications/{id}
- POST /api/medications/{id}/log

### Appointments
- GET /api/appointments/{user_id}
- POST /api/appointments
- PUT /api/appointments/{id}
- DELETE /api/appointments/{id}

### Tasks
- GET /api/tasks/{user_id}
- POST /api/tasks
- PUT /api/tasks/{id}
- DELETE /api/tasks/{id}

### Caregiver Dashboard
- GET /api/caregiver/{caregiver_id}/elders
- GET /api/caregiver/{elder_id}/reports
- GET /api/caregiver/{elder_id}/alerts

### AI Integration
- POST /api/ai/chat
- POST /api/ai/transcribe
- GET /api/ai/mood-analysis/{user_id}

### Third-Party Integrations
- POST /api/integrations/uber/book
- GET /api/integrations/calendar/events
- POST /api/integrations/health/sync

## Security Considerations

### Data Protection
- All sensitive data encrypted at rest
- HTTPS/TLS for all communications
- JWT tokens with short expiration
- Input validation and sanitization
- Rate limiting on API endpoints

### Privacy Compliance
- GDPR compliance for EU users
- HIPAA considerations for health data
- User consent management
- Data retention policies
- Right to deletion implementation

### Access Control
- Role-based access (Elder, Caregiver, Admin)
- API key management for third-party services
- Audit logging for sensitive operations
- Multi-factor authentication option

## AI Conversation Design

### Personality Traits
- Warm, patient, and understanding
- Uses simple, clear language
- Remembers previous conversations
- Proactive but not intrusive
- Culturally sensitive

### Core Conversation Flows
1. **Daily Check-ins**: "Good morning! How are you feeling today?"
2. **Medication Reminders**: "It's time for your morning pills. Have you taken them?"
3. **Appointment Preparation**: "Your doctor's appointment is tomorrow at 2 PM. Shall I book a ride?"
4. **Emotional Support**: "You seem a bit down today. Would you like to talk about it?"
5. **Emergency Detection**: "I noticed you mentioned feeling unwell. Should I contact your caregiver?"

### Proactive Features
- Daily wellness checks
- Medication adherence monitoring
- Appointment reminders (24h, 2h, 30min before)
- Weather updates and clothing suggestions
- Social engagement prompts
- Emergency situation detection

