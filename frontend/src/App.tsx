import { useState, useEffect, useRef } from 'react'
import './App.css'

interface Agent {
  id: string
  name: string
  emoji?: string
  avatar?: string
}

interface Message {
  id: string
  sender: string
  senderName: string
  content: string
  timestamp: Date
  type: 'sent' | 'received' | 'system'
}

function App() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Fetch agents on mount
    fetch('/api/agents')
      .then(res => res.json())
      .then(data => setAgents(data.agents || []))
      .catch(console.error)

    // Connect WebSocket
    const socket = new WebSocket(`ws://${window.location.host}/ws/user`)

    socket.onopen = () => {
      console.log('WebSocket connected')
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: data.client_id,
          senderName: data.client_id,
          content: data.message,
          timestamp: new Date(),
          type: 'received'
        }])
      } catch (e) {
        // Handle non-JSON messages
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: 'system',
          senderName: 'System',
          content: event.data,
          timestamp: new Date(),
          type: 'system'
        }])
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    setWs(socket)

    return () => socket.close()
  }, [])

  const sendMessage = async () => {
    if (!input.trim()) return

    const messageText = input.trim()
    const currentAgent = selectedAgent

    // Add user's message to the chat immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      senderName: 'You',
      content: messageText,
      timestamp: new Date(),
      type: 'sent'
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')

    // Also broadcast via WebSocket for real-time sync
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(messageText)
    }

    // If an agent is selected, send to that agent via API
    if (currentAgent) {
      setIsLoading(true)
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: messageText,
            agent_id: currentAgent
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const result = await response.json()

        // Add agent's response to the chat
        const agentResponse: Message = {
          id: (Date.now() + 1).toString(),
          sender: currentAgent,
          senderName: currentAgent,
          content: result.response || result.message || JSON.stringify(result),
          timestamp: new Date(),
          type: 'received'
        }
        setMessages(prev => [...prev, agentResponse])
      } catch (error) {
        console.error('Failed to send to agent:', error)
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'system',
          senderName: 'System',
          content: `Failed to send message to ${currentAgent}: ${error instanceof Error ? error.message : 'Unknown error'}`,
          timestamp: new Date(),
          type: 'system'
        }
        setMessages(prev => [...prev, errorMessage])
      } finally {
        setIsLoading(false)
      }
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>🤖 OpenCLAW</h1>
          <div className="subtitle">Multi-Agent Chat</div>
        </div>

        <div className="agent-list">
          <div className="agent-list-title">Available Agents</div>
          {agents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">😔</div>
              <div className="empty-state-text">No agents available</div>
            </div>
          ) : (
            agents.map(agent => (
              <div
                key={agent.id}
                className={`agent-item ${selectedAgent === agent.id ? 'active' : ''}`}
                onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
              >
                <div className="agent-avatar">
                  {agent.emoji || '🤖'}
                </div>
                <div className="agent-info">
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-status">
                    <span className="status-dot"></span>
                    Online
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-header-title">
            {selectedAgent ? `Chat with ${selectedAgent}` : 'General Chat'}
          </div>
          <div className="chat-header-subtitle">
            {selectedAgent
              ? `Sending messages directly to ${selectedAgent}`
              : 'Broadcasting to all connected clients'}
          </div>
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <div className="empty-state-text">
                No messages yet. Select an agent and start chatting!
              </div>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className={`message ${msg.type}`}>
                {msg.type !== 'sent' && (
                  <div className="message-meta">
                    <span className="message-sender">{msg.senderName}</span>
                    <span className="message-time">{formatTime(msg.timestamp)}</span>
                  </div>
                )}
                <div className="message-bubble">{msg.content}</div>
                {msg.type === 'sent' && (
                  <div className="message-meta">
                    <span className="message-time">{formatTime(msg.timestamp)}</span>
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          {agents.length > 0 && (
            <div className="agent-selector">
              {agents.slice(0, 5).map(agent => (
                <div
                  key={agent.id}
                  className={`agent-chip ${selectedAgent === agent.id ? 'selected' : ''}`}
                  onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                >
                  <span className="agent-chip-emoji">{agent.emoji || '🤖'}</span>
                  {agent.name}
                </div>
              ))}
              {agents.length > 5 && (
                <div className="agent-chip">+{agents.length - 5} more</div>
              )}
            </div>
          )}
          <div className="input-wrapper">
            <input
              type="text"
              className="message-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
              placeholder={selectedAgent
                ? `Message ${selectedAgent}...`
                : 'Type a message... (select agent to trigger bot)'}
              disabled={isLoading}
            />
            <button
              className="send-button"
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App