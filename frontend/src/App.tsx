import { useState, useEffect } from 'react'

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
}

function App() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [ws, setWs] = useState<WebSocket | null>(null)

  useEffect(() => {
    // Fetch agents on mount
    fetch('/api/agents')
      .then(res => res.json())
      .then(data => setAgents(data.agents || []))
      .catch(console.error)

    // Connect WebSocket
    const socket = new WebSocket(`ws://${window.location.host}/ws/user`)
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: data.client_id,
        senderName: data.client_id,
        content: data.message,
        timestamp: new Date()
      }])
    }
    
    setWs(socket)
    
    return () => socket.close()
  }, [])

  const sendMessage = () => {
    if (!input.trim() || !ws) return
    
    ws.send(input)
    setInput('')
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Agent List Sidebar */}
      <div style={{ width: '250px', borderRight: '1px solid #ccc', padding: '16px' }}>
        <h2>Agents</h2>
        {agents.length === 0 ? (
          <p>No agents available</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {agents.map(agent => (
              <li key={agent.id} style={{ padding: '8px', marginBottom: '8px', background: '#f5f5f5', borderRadius: '8px' }}>
                <span style={{ fontSize: '24px' }}>{agent.emoji || '🤖'}</span>
                <span style={{ marginLeft: '8px' }}>{agent.name}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
          {messages.map(msg => (
            <div key={msg.id} style={{ marginBottom: '12px', padding: '8px', background: '#f0f0f0', borderRadius: '8px' }}>
              <strong>{msg.senderName}:</strong> {msg.content}
            </div>
          ))}
        </div>
        
        {/* Input Area */}
        <div style={{ padding: '16px', borderTop: '1px solid #ccc', display: 'flex' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message... (use @agent to mention)"
            style={{ flex: 1, padding: '8px', fontSize: '16px' }}
          />
          <button onClick={sendMessage} style={{ padding: '8px 16px', marginLeft: '8px' }}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
