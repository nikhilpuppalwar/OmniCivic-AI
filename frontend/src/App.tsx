import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Activity, FileText, Settings as SettingsIcon, Sun, Moon, Sparkles } from 'lucide-react';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import CitizenReport from './pages/CitizenReport';
import Settings from './pages/Settings';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import './index.css';


function AppShell() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Navigation */}
      <nav style={{
        background: 'var(--bg-secondary)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border-primary)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        height: 56,
        position: 'sticky',
        top: 0,
        zIndex: 50,
        transition: 'all 0.2s ease',
      }}>
        <NavLink to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 10, marginRight: 24 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'linear-gradient(135deg, #2563EB 0%, #0D9488 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px rgba(37, 99, 235, 0.4)',
          }}>
            <Activity size={18} color="#ffffff" />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ fontWeight: 800, fontSize: 16, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                OmniCivic AI
              </span>
              <span style={{
                fontSize: 9,
                color: 'var(--accent-blue)',
                background: 'rgba(37, 99, 235, 0.1)',
                border: '1px solid rgba(37, 99, 235, 0.25)',
                padding: '1px 6px',
                borderRadius: 4,
                fontWeight: 700,
                letterSpacing: '0.05em',
              }}>
                INTELLIGENCE
              </span>
            </div>
            <span style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>
              Autonomous Municipal Incident Operations
            </span>
          </div>
        </NavLink>


        <div style={{ display: 'flex', gap: 6 }}>
          <NavLink to="/" end style={({ isActive }) => ({
            padding: '7px 14px',
            borderRadius: 6,
            fontSize: 13,
            fontWeight: 600,
            color: isActive ? '#ffffff' : 'var(--text-secondary)',
            background: isActive ? 'var(--accent-blue)' : 'transparent',
            border: `1px solid ${isActive ? 'var(--accent-blue)' : 'transparent'}`,
            boxShadow: isActive ? '0 0 12px rgba(37, 99, 235, 0.3)' : 'none',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'all 0.15s ease',
          })}>
            <Sparkles size={14} />
            Overview
          </NavLink>
          <NavLink to="/dashboard" style={({ isActive }) => ({
            padding: '7px 14px',
            borderRadius: 6,
            fontSize: 13,
            fontWeight: 600,
            color: isActive ? '#ffffff' : 'var(--text-secondary)',
            background: isActive ? 'var(--accent-blue)' : 'transparent',
            border: `1px solid ${isActive ? 'var(--accent-blue)' : 'transparent'}`,
            boxShadow: isActive ? '0 0 12px rgba(37, 99, 235, 0.3)' : 'none',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'all 0.15s ease',
          })}>
            <Activity size={14} />
            Operations Dashboard
          </NavLink>
          <NavLink to="/report" style={({ isActive }) => ({
            padding: '7px 14px',
            borderRadius: 6,
            fontSize: 13,
            fontWeight: 600,
            color: isActive ? '#ffffff' : 'var(--text-secondary)',
            background: isActive ? 'var(--accent-blue)' : 'transparent',
            border: `1px solid ${isActive ? 'var(--accent-blue)' : 'transparent'}`,
            boxShadow: isActive ? '0 0 12px rgba(37, 99, 235, 0.3)' : 'none',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'all 0.15s ease',
          })}>
            <FileText size={14} />
            Citizen Portal
          </NavLink>
          <NavLink to="/settings" style={({ isActive }) => ({
            padding: '7px 14px',
            borderRadius: 6,
            fontSize: 13,
            fontWeight: 600,
            color: isActive ? '#ffffff' : 'var(--text-secondary)',
            background: isActive ? 'var(--accent-blue)' : 'transparent',
            border: `1px solid ${isActive ? 'var(--accent-blue)' : 'transparent'}`,
            boxShadow: isActive ? '0 0 12px rgba(37, 99, 235, 0.3)' : 'none',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            transition: 'all 0.15s ease',
          })}>
            <SettingsIcon size={14} />
            AI Settings
          </NavLink>
        </div>


        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 16 }}>
          {/* Live System Status Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            borderRadius: 20,
            fontSize: 11,
            fontWeight: 500,
            color: '#10B981',
          }}>
            <span style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              backgroundColor: '#10B981',
              boxShadow: '0 0 8px #10B981',
              animation: 'pulse-dot 1.5s infinite',
            }}></span>
            AI Engine Operational
          </div>

          {/* Light / Dark mode toggle */}
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </nav>


      {/* Routes */}
      <main style={{ flex: 1, padding: '20px 24px' }}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/report" element={<CitizenReport />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>

      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-primary)',
        padding: '10px 24px',
        fontSize: 11,
        color: 'var(--text-tertiary)',
        textAlign: 'center',
        transition: 'border-color 0.2s ease',
      }}>
        Prototype uses synthetic civic data for demonstration. All root-cause output is AI-generated civic incident hypothesis.
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </ThemeProvider>
  );
}
