# Elder Care AI App MVP - UI/UX Design Specifications

## Design Principles

### Accessibility First
- **Large Typography**: Minimum 18px font size, scalable up to 24px
- **High Contrast**: Dark text on light backgrounds, WCAG AA compliance
- **Simple Navigation**: Single-screen focus, minimal cognitive load
- **Touch-Friendly**: Minimum 44px touch targets, generous spacing
- **Voice-First**: Every action accessible via voice commands

### Elderly-Friendly Features
- **Simplified Interface**: Chat-only primary interface
- **Clear Visual Hierarchy**: Important elements prominently displayed
- **Consistent Patterns**: Predictable layouts and interactions
- **Error Prevention**: Confirmation dialogs for important actions
- **Gentle Feedback**: Soft animations, reassuring messages

## Mobile App Wireframes

### Main Chat Interface
```
┌─────────────────────────────────────┐
│ ☰  Elder Care Assistant        🔊   │
├─────────────────────────────────────┤
│                                     │
│  AI: Good morning, Mary! How are    │
│      you feeling today?             │
│                                     │
│                     You: I'm fine   │
│                     thank you       │
│                                     │
│  AI: That's wonderful! Don't       │
│      forget your morning pills.     │
│      Have you taken them?           │
│                                     │
│                     You: Not yet    │
│                                     │
│  AI: No worries! I'll remind you   │
│      in 10 minutes. 💊             │
│                                     │
├─────────────────────────────────────┤
│ [Type your message...]        🎤 📤 │
└─────────────────────────────────────┘
```

### Medication Reminder Screen
```
┌─────────────────────────────────────┐
│ ← Medication Reminder               │
├─────────────────────────────────────┤
│                                     │
│           💊                        │
│                                     │
│     Time for your morning pills!    │
│                                     │
│     • Lisinopril 10mg              │
│     • Metformin 500mg               │
│                                     │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │         I've taken them         │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Remind me later          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │         I need help             │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Appointment Reminder
```
┌─────────────────────────────────────┐
│ ← Upcoming Appointment              │
├─────────────────────────────────────┤
│                                     │
│           🏥                        │
│                                     │
│    Dr. Johnson - Cardiology         │
│    Tomorrow at 2:00 PM              │
│    City Medical Center              │
│                                     │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Book my ride             │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │      I have my own ride         │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │       Reschedule                │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Voice Recording Interface
```
┌─────────────────────────────────────┐
│ ← Recording Appointment Notes       │
├─────────────────────────────────────┤
│                                     │
│                                     │
│           🎤                        │
│                                     │
│      Recording your visit...        │
│                                     │
│         ●●●●●●●●●●                  │
│                                     │
│        00:02:34                     │
│                                     │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │         Stop Recording          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │           Pause                 │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

## Caregiver Dashboard Wireframes

### Dashboard Overview
```
┌─────────────────────────────────────────────────────────────┐
│ Elder Care Dashboard - Mary's Health Summary                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │   Today's   │ │ Medication  │ │ Mood Score  │ │ Alerts  │ │
│ │ Interactions│ │ Compliance  │ │             │ │         │ │
│ │     12      │ │    95%      │ │    8/10     │ │    2    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│                                                             │
│ Recent Conversations:                                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 9:30 AM - Morning check-in completed                   │ │
│ │ 10:15 AM - Medication reminder acknowledged            │ │
│ │ 2:45 PM - Expressed feeling lonely                     │ │
│ │ 4:20 PM - Appointment reminder for tomorrow            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Upcoming Appointments:                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Tomorrow 2:00 PM - Dr. Johnson (Cardiology)            │ │
│ │ Friday 10:30 AM - Physical Therapy                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Health Report
```
┌─────────────────────────────────────────────────────────────┐
│ Weekly Health Report - March 10-16, 2025                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Medication Compliance:                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Mon ████████████████████████████████████████████ 100%  │ │
│ │ Tue ████████████████████████████████████████████ 100%  │ │
│ │ Wed ████████████████████████████████████████████ 100%  │ │
│ │ Thu ████████████████████████████████████████████ 100%  │ │
│ │ Fri ████████████████████████████████████████████ 100%  │ │
│ │ Sat ████████████████████████████████████████████ 100%  │ │
│ │ Sun ████████████████████████████████████████████ 100%  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Mood Tracking:                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │     10 ┌─┐                                              │ │
│ │      9 │ │     ┌─┐                                      │ │
│ │      8 │ │ ┌─┐ │ │ ┌─┐                                  │ │
│ │      7 │ │ │ │ │ │ │ │     ┌─┐                          │ │
│ │      6 │ │ │ │ │ │ │ │ ┌─┐ │ │                          │ │
│ │      5 │ │ │ │ │ │ │ │ │ │ │ │                          │ │
│ │        Mon Tue Wed Thu Fri Sat Sun                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ AI Insights:                                               │
│ • Mary has been consistently taking medications            │
│ • Mood slightly lower on weekends - may need more social   │
│   engagement                                               │
│ • Expressed concern about upcoming cardiology appointment  │ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Primary Colors
- **Background**: #FFFFFF (Pure White)
- **Primary Text**: #2C3E50 (Dark Blue-Gray)
- **Secondary Text**: #7F8C8D (Medium Gray)
- **AI Messages**: #E8F4FD (Light Blue Background)
- **User Messages**: #F8F9FA (Light Gray Background)

### Accent Colors
- **Primary Action**: #3498DB (Blue)
- **Success**: #27AE60 (Green)
- **Warning**: #F39C12 (Orange)
- **Error**: #E74C3C (Red)
- **Medication**: #9B59B6 (Purple)
- **Appointment**: #1ABC9C (Teal)

### Typography
- **Primary Font**: System fonts (San Francisco on iOS, Roboto on Android)
- **Fallback**: Arial, sans-serif
- **Sizes**: 
  - Heading: 24px (bold)
  - Body: 18px (regular)
  - Small: 16px (regular)
  - Button: 20px (medium)

## Interaction Patterns

### Voice Commands
- "Take me to my medications"
- "Show my appointments"
- "Call my caregiver"
- "Record appointment notes"
- "How am I doing this week?"

### Gesture Support
- **Swipe Right**: Go back to previous screen
- **Long Press**: Access voice recording
- **Double Tap**: Confirm action
- **Pinch to Zoom**: Increase text size

### Feedback Mechanisms
- **Haptic Feedback**: For button presses and confirmations
- **Audio Cues**: Success sounds, gentle notification chimes
- **Visual Feedback**: Button state changes, loading indicators
- **Voice Confirmation**: AI acknowledges all user actions

