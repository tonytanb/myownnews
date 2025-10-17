import React from 'react';
import './App.css';
import AudioPlayer from './components/AudioPlayer';

const App: React.FC = () => {


  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">CURIO</div>
        <div className="header-actions">
          <button className="menu-btn">☰</button>
          <button className="settings-btn">⚙️</button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="date-header">
          📅 {new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>

        <div className="title-section">
          <h1>Today's Brief</h1>
          <p className="subtitle">Your world in 5 minutes</p>
        </div>

        {/* Judge-Friendly Audio Player */}
        <div className="demo-section">
          <h2>🎧 Agent-Powered News Demo</h2>
          <p>Click below to experience our AI-curated news briefing with full provenance tracking</p>
          <AudioPlayer />
        </div>
      </main>
    </div>
  );
};

export default App;