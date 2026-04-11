import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null)
  const [profile, setProfile] = useState(null)
  const [attendance, setAttendance] = useState([])
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Navigation State
  const [currentScreen, setCurrentScreen] = useState('home')

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      })

      if (!res.ok) throw new Error('Invalid credentials')
      const data = await res.json()
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!token) return
    const fetchData = async () => {
      try {
        const profRes = await fetch(`${API_BASE}/auth/profile`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (profRes.ok) setProfile(await profRes.json())

        const attRes = await fetch(`${API_BASE}/student/attendance`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (attRes.ok) setAttendance(await attRes.json())
      } catch (err) {}
    }
    fetchData()
  }, [token])

  const calculateAttendance = () => {
    if (!attendance.length) return 0
    const conducted = attendance.filter(a => a.status !== "NC" && a.date !== null)
    const presentCount = conducted.filter(a => a.status === "Present").length
    return conducted.length > 0 ? Math.round((presentCount / conducted.length) * 100) : 0
  }

  const attPercent = calculateAttendance()

  if (!token) {
    return (
      <div className="mobile-app-frame">
        <div className="login-screen">
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h1 style={{ color: 'var(--primary)', fontWeight: 800 }}>AuraFace</h1>
            <p style={{ color: 'var(--text-sub)' }}>Sign in to continue</p>
          </div>
          <form onSubmit={handleLogin}>
            <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required 
                   className="login-input" />
            <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required 
                   className="login-input" />
            {error && <p style={{ color: '#EF4444', marginBottom: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>{error}</p>}
            <button className="primary-btn" type="submit" disabled={loading}>
              {loading ? 'Signing In...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  // --- SUB-SCREENS ---
  const renderDigitalID = () => (
    <div className="scroll-area" style={{ padding: '2rem' }}>
      <div style={{ background: 'linear-gradient(to right, #0D47A1, #1976D2)', padding: '1rem', borderRadius: '20px 20px 0 0', color: 'white', textAlign: 'center' }}>
        <h3 style={{ fontSize: '1rem' }}>GANDHI INSTITUTE OF ENG. AND TECH</h3>
        <p style={{ color: '#FFD700', fontSize: '0.8rem', fontWeight: 600 }}>STUDENT IDENTITY CARD</p>
      </div>
      <div style={{ background: 'white', padding: '2rem 1rem', borderRadius: '0 0 20px 20px', textAlign: 'center', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: '#e2e8f0', margin: '-50px auto 1rem', border: '4px solid #0D47A1', backgroundImage: profile?.profile_image ? `url(${API_BASE}${profile.profile_image})` : 'none', backgroundSize: 'cover' }}></div>
        <h2>{profile?.name || 'STUDENT'}</h2>
        <p style={{ color: 'var(--text-sub)' }}>{profile?.department || 'CSE'} - {profile?.program || 'B.Tech'}</p>
        <div style={{ marginTop: '2rem', textAlign: 'left', padding: '0 1rem' }}>
          <p><strong>Roll No:</strong> {profile?.roll_no || 'N/A'}</p>
          <p><strong>Session:</strong> Year {profile?.year || 'N/A'} (Sem {profile?.semester || 'N/A'})</p>
          <p><strong>Blood Group:</strong> {profile?.blood_group || 'N/A'}</p>
        </div>
      </div>
    </div>
  )

  const renderAttendanceHistory = () => (
    <div className="scroll-area" style={{ padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem' }}>Overall: {attPercent}%</h3>
      {attendance.map((record, i) => (
        <div key={i} className="dashboard-card" style={{ margin: '0 0 0.5rem 0', borderLeft: `6px solid ${record.status === 'Present' ? '#10B981' : record.status === 'Absent' ? '#EF4444' : '#CBD5E1'}` }}>
          <div className="card-content">
            <div className="card-title">{record.subject}</div>
            <div className="card-subtitle">{record.date || 'Not Scheduled'}</div>
          </div>
          <div style={{ fontWeight: 'bold', color: record.status === 'Present' ? '#10B981' : record.status === 'Absent' ? '#EF4444' : '#94A3B8' }}>
            {record.status}
          </div>
        </div>
      ))}
    </div>
  )

  const renderHome = () => (
    <div className="scroll-area">
      <div className="stats-header">
        <p style={{ fontSize: '1rem', opacity: 0.9 }}>Overall Attendance</p>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, margin: '0.5rem 0' }}>{attPercent}%</h1>
        <div className="progress-bar-container">
          <div className="progress-bar-fill" style={{ width: `${attPercent}%`, backgroundColor: attPercent >= 75 ? '#10B981' : '#EF4444' }}></div>
        </div>
      </div>

      <h3 className="section-header">Core Academics</h3>

      <div className="dashboard-card active-ripple" onClick={() => setCurrentScreen('id')}>
        <div className="icon-circle" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#F59E0B' }}>🆔</div>
        <div className="card-content">
          <div className="card-title">Digital Campus ID</div>
          <div className="card-subtitle">View your smart ID card</div>
        </div>
        <div style={{ color: '#CBD5E1' }}>›</div>
      </div>

      <div className="dashboard-card active-ripple" onClick={() => setCurrentScreen('timetable')}>
        <div className="icon-circle" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3B82F6' }}>📅</div>
        <div className="card-content">
          <div className="card-title">View Timetable</div>
          <div className="card-subtitle">Check your daily class schedule</div>
        </div>
        <div style={{ color: '#CBD5E1' }}>›</div>
      </div>

      <div className="dashboard-card active-ripple" onClick={() => setCurrentScreen('attendance')}>
        <div className="icon-circle" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10B981' }}>✅</div>
        <div className="card-content">
          <div className="card-title">Attendance History</div>
          <div className="card-subtitle">Detailed subject-wise records</div>
        </div>
        <div style={{ color: '#CBD5E1' }}>›</div>
      </div>

      <div className="dashboard-card active-ripple">
        <div className="icon-circle" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#F59E0B' }}>📝</div>
        <div className="card-content">
          <div className="card-title">Request Leave</div>
          <div className="card-subtitle">Apply for official absences</div>
        </div>
        <div style={{ color: '#CBD5E1' }}>›</div>
      </div>

      <h3 className="section-header">Smart Features</h3>
      <div className="dashboard-card active-ripple">
        <div className="icon-circle" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10B981' }}>📚</div>
        <div className="card-content">
          <div className="card-title">Smart E-Library</div>
          <div className="card-subtitle">Access books, notes, and past papers</div>
        </div>
        <div style={{ color: '#CBD5E1' }}>›</div>
      </div>
    </div>
  )

  const screenTitles = {
    'home': 'My Progress',
    'id': 'Digital Campus ID',
    'attendance': 'Attendance History',
    'timetable': 'Timetable'
  }

  return (
    <div className="mobile-app-frame">
      <div className="top-bar">
        {currentScreen !== 'home' ? (
          <span style={{ fontSize: '1.5rem', cursor: 'pointer', paddingRight: '1rem' }} onClick={() => setCurrentScreen('home')}>←</span>
        ) : (
          <span style={{ fontSize: '1.5rem', cursor: 'pointer', paddingRight: '1rem' }} onClick={() => { setToken(null); localStorage.removeItem('token'); }}>←</span>
        )}
        <h2>{screenTitles[currentScreen] || 'AuraFace'}</h2>
      </div>

      {currentScreen === 'home' && renderHome()}
      {currentScreen === 'id' && renderDigitalID()}
      {currentScreen === 'attendance' && renderAttendanceHistory()}
      {currentScreen === 'timetable' && <div style={{padding: '2rem', textAlign: 'center'}}>Timetable UI Loading...</div>}

      <div className="bottom-nav">
        <div className={`nav-item ${currentScreen === 'home' ? 'active' : ''}`} onClick={() => setCurrentScreen('home')}>
          <span style={{ fontSize: '1.5rem' }}>🏠</span>
          <span>Home</span>
        </div>
        <div className={`nav-item ${currentScreen === 'timetable' ? 'active' : ''}`} onClick={() => setCurrentScreen('timetable')}>
          <span style={{ fontSize: '1.5rem' }}>📅</span>
          <span>Schedule</span>
        </div>
        <div className={`nav-item ${currentScreen === 'profile' ? 'active' : ''}`} onClick={() => setCurrentScreen('profile')}>
          <span style={{ fontSize: '1.5rem' }}>👤</span>
          <span>Profile</span>
        </div>
      </div>
    </div>
  )
}

export default App
