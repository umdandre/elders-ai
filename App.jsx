import { useState, useEffect, useRef, createContext, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  MessageCircle, 
  Mic, 
  MicOff, 
  Send, 
  Pill, 
  Calendar, 
  Heart, 
  Menu,
  Phone,
  Settings,
  User
} from 'lucide-react'
import './App.css'

// Mock API service
const API_BASE = 'http://localhost:5001/api'

const apiService = {
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      return response.json()
    } catch (error) {
      return { error: 'Connection failed' }
    }
  },
  
  async getConversations(userId, token) {
    try {
      const response = await fetch(`${API_BASE}/conversations/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      return response.json()
    } catch (error) {
      return { error: 'Connection failed' }
    }
  },
  
  async sendMessage(message, token) {
    try {
      const response = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(message)
      })
      return response.json()
    } catch (error) {
      return { error: 'Connection failed' }
    }
  }
}

// Authentication Context
const AuthContext = createContext()

function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  
  useEffect(() => {
    if (token) {
      // Verify token and get user info
      const userData = JSON.parse(localStorage.getItem('user') || '{}')
      setUser(userData)
    }
  }, [token])
  
  const login = async (email, password) => {
    try {
      const response = await apiService.login(email, password)
      if (response.token) {
        setToken(response.token)
        setUser(response.user)
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
        return { success: true }
      }
      return { success: false, error: response.error }
    } catch (error) {
      return { success: false, error: 'Connection failed' }
    }
  }
  
  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Login Component
function LoginScreen() {
  const [email, setEmail] = useState('mary@example.com')
  const [password, setPassword] = useState('password123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useContext(AuthContext)
  
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    const result = await login(email, password)
    if (!result.success) {
      setError(result.error || 'Login failed')
    }
    setLoading(false)
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
      <Card className="elder-card w-full max-w-md">
        <div className="text-center mb-8">
          <Heart className="w-16 h-16 text-primary mx-auto mb-4" />
          <h1 className="elder-text-large text-primary">Elder Care Assistant</h1>
          <p className="elder-text text-muted-foreground mt-2">Your caring companion</p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="elder-text block mb-2">Email</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="elder-input"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div>
            <label className="elder-text block mb-2">Password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="elder-input"
              placeholder="Enter your password"
              required
            />
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="elder-text text-red-600">{error}</p>
            </div>
          )}
          
          <Button 
            type="submit" 
            className="elder-button w-full"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="elder-text text-sm text-center text-blue-700">
            Demo Account: mary@example.com / password123
          </p>
        </div>
      </Card>
    </div>
  )
}

// Chat Message Component
function ChatMessage({ message, isAI }) {
  return (
    <div className={`message-bubble ${isAI ? 'message-ai' : 'message-user'}`}>
      <p>{message.text}</p>
      <div className="text-xs opacity-70 mt-2 flex justify-between">
        <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
        {message.mood_score && (
          <span className="text-blue-600">Mood: {message.mood_score}/10</span>
        )}
      </div>
    </div>
  )
}

// Voice Recording Component
function VoiceRecorder({ onRecordingComplete, isRecording, setIsRecording }) {
  const [recordingTime, setRecordingTime] = useState(0)
  const intervalRef = useRef()
  
  useEffect(() => {
    if (isRecording) {
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } else {
      clearInterval(intervalRef.current)
      setRecordingTime(0)
    }
    
    return () => clearInterval(intervalRef.current)
  }, [isRecording])
  
  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false)
      onRecordingComplete(`Voice message recorded (${recordingTime}s)`)
    } else {
      setIsRecording(true)
    }
  }
  
  if (isRecording) {
    return (
      <div className="voice-recording p-4 rounded-lg text-center">
        <Mic className="w-8 h-8 text-red-500 mx-auto mb-2 pulse" />
        <p className="elder-text text-red-600">Recording... {recordingTime}s</p>
        <Button 
          onClick={toggleRecording}
          className="elder-button mt-4 bg-red-500 hover:bg-red-600"
        >
          <MicOff className="w-5 h-5 mr-2" />
          Stop Recording
        </Button>
      </div>
    )
  }
  
  return (
    <Button 
      onClick={toggleRecording}
      className="elder-button bg-blue-500 hover:bg-blue-600"
    >
      <Mic className="w-5 h-5 mr-2" />
      Voice Message
    </Button>
  )
}

// Quick Actions Component
function QuickActions({ onActionClick }) {
  const actions = [
    { icon: Pill, label: 'Medications', color: 'bg-purple-500', action: 'medications' },
    { icon: Calendar, label: 'Appointments', color: 'bg-teal-500', action: 'appointments' },
    { icon: Phone, label: 'Call Help', color: 'bg-red-500', action: 'emergency' },
    { icon: Heart, label: 'How I Feel', color: 'bg-pink-500', action: 'mood' }
  ]
  
  return (
    <div className="grid grid-cols-2 gap-4 p-4">
      {actions.map((action, index) => (
        <Button
          key={index}
          onClick={() => onActionClick(action.action)}
          className={`elder-button ${action.color} hover:opacity-90 text-white flex flex-col items-center space-y-2 h-20`}
        >
          <action.icon className="w-6 h-6" />
          <span className="text-sm">{action.label}</span>
        </Button>
      ))}
    </div>
  )
}

// Main Chat Interface
function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Good morning! I'm your AI companion. How are you feeling today?",
      isAI: true,
      timestamp: new Date().toISOString()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [showQuickActions, setShowQuickActions] = useState(true)
  const messagesEndRef = useRef(null)
  const { user, token, logout } = useContext(AuthContext)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const sendMessage = async (text, isVoice = false) => {
    if (!text.trim()) return
    
    const userMessage = {
      id: Date.now(),
      text: text,
      isAI: false,
      timestamp: new Date().toISOString(),
      isVoice
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setShowQuickActions(false)
    
    // Send to AI backend
    try {
      const response = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: text })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        const aiMessage = {
          id: Date.now() + 1,
          text: data.response,
          isAI: true,
          timestamp: new Date().toISOString(),
          mood_score: data.mood_score,
          contains_concern: data.contains_concern
        }
        setMessages(prev => [...prev, aiMessage])
      } else {
        // Fallback to simulated response
        const aiResponse = generateAIResponse(text)
        const aiMessage = {
          id: Date.now() + 1,
          text: aiResponse,
          isAI: true,
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      // Fallback to simulated response
      const aiResponse = generateAIResponse(text)
      const aiMessage = {
        id: Date.now() + 1,
        text: aiResponse,
        isAI: true,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, aiMessage])
    }
  }
  
  const generateAIResponse = (userText) => {
    const responses = {
      'medications': "It's time for your morning pills! You have Lisinopril 10mg and Metformin 500mg. Have you taken them today?",
      'appointments': "You have an appointment with Dr. Johnson tomorrow at 2:00 PM for your cardiology check-up. Would you like me to book a ride?",
      'emergency': "I'm here to help! If this is a medical emergency, please call 911. Otherwise, I can contact your caregiver Sarah. What would you like me to do?",
      'mood': "I'm glad you want to share how you're feeling. On a scale of 1 to 10, how would you rate your mood today? Remember, it's okay to have ups and downs.",
      'default': "I understand. Is there anything specific I can help you with today? I can remind you about medications, appointments, or just chat with you."
    }
    
    const lowerText = userText.toLowerCase()
    if (lowerText.includes('pill') || lowerText.includes('medication')) return responses.medications
    if (lowerText.includes('appointment') || lowerText.includes('doctor')) return responses.appointments
    if (lowerText.includes('help') || lowerText.includes('emergency')) return responses.emergency
    if (lowerText.includes('feel') || lowerText.includes('mood')) return responses.mood
    
    return responses.default
  }
  
  const handleQuickAction = (action) => {
    const actionTexts = {
      'medications': 'Show me my medications',
      'appointments': 'What are my upcoming appointments?',
      'emergency': 'I need help',
      'mood': 'I want to talk about how I feel'
    }
    
    sendMessage(actionTexts[action])
  }
  
  const handleVoiceRecording = (text) => {
    sendMessage(text, true)
  }
  
  return (
    <div className="chat-container flex flex-col">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Heart className="w-8 h-8" />
          <div>
            <h1 className="elder-text-large">Hello, {user?.full_name || 'Friend'}</h1>
            <p className="text-sm opacity-90">Your AI Companion</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="sm" className="text-white">
            <Settings className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="sm" onClick={logout} className="text-white">
            <User className="w-5 h-5" />
          </Button>
        </div>
      </div>
      
      {/* Messages */}
      <div className="chat-messages">
        {messages.map((message) => (
          <ChatMessage 
            key={message.id} 
            message={message} 
            isAI={message.isAI} 
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Quick Actions */}
      {showQuickActions && (
        <div className="border-t border-border">
          <div className="p-4">
            <p className="elder-text text-center text-muted-foreground mb-4">
              How can I help you today?
            </p>
            <QuickActions onActionClick={handleQuickAction} />
          </div>
        </div>
      )}
      
      {/* Input Area */}
      <div className="chat-input-container">
        {isRecording ? (
          <VoiceRecorder 
            onRecordingComplete={handleVoiceRecording}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
          />
        ) : (
          <div className="flex items-center space-x-3">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputText)}
              placeholder="Type your message..."
              className="elder-input flex-1"
            />
            <Button 
              onClick={() => setIsRecording(true)}
              className="elder-button bg-blue-500 hover:bg-blue-600 px-4"
            >
              <Mic className="w-5 h-5" />
            </Button>
            <Button 
              onClick={() => sendMessage(inputText)}
              className="elder-button bg-primary hover:bg-primary/90 px-4"
              disabled={!inputText.trim()}
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

// Protected Route Component
function ProtectedRoute({ children }) {
  const { token } = useContext(AuthContext)
  
  if (!token) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            <Route path="/login" element={<LoginScreen />} />
            <Route path="/chat" element={<ProtectedRoute><ChatInterface /></ProtectedRoute>} />
            <Route path="/" element={<Navigate to="/chat" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

