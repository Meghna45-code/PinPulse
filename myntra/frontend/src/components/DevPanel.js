import React from 'react';

function DevPanel({ state, zipCode, devLog, onSetState, onSetZip, onTimeWarp, onVelocitySurge, onSetFestival, onReset }) {
  const states = ['discovery', 'high_intent', 'festive_season', 'hyper_local_boutique', 'social_commerce'];
  const zips = [
    { code: '800008', city: 'Patna' },
    { code: '530001', city: 'Vizag' },
    { code: '641001', city: 'Coimbatore' },
    { code: '590001', city: 'Belgaum' },
    { code: '110001', city: 'Delhi' },
  ];
  const festivals = ['chhath_puja', 'diwali', 'pongal', 'eid'];

  return (
    <div className="dev-panel">
      <div className="dev-panel-header">
        <h2>⚙️ Dev Panel (Judge View)</h2>
        <button className="btn-reset" onClick={onReset}>🔄 Reset All</button>
      </div>

      {/* State Machine Controls */}
      <div className="dev-section">
        <h3>🎯 State Machine</h3>
        <p className="dev-label">Current: <strong>{state}</strong></p>
        <div className="dev-buttons">
          {states.map(s => (
            <button
              key={s}
              className={`dev-btn ${state === s ? 'active' : ''}`}
              onClick={() => onSetState(s)}
            >
              {s.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* ZIP Code Controls */}
      <div className="dev-section">
        <h3>📍 Location (ZIP Code)</h3>
        <div className="dev-buttons">
          {zips.map(z => (
            <button
              key={z.code}
              className={`dev-btn ${zipCode === z.code ? 'active' : ''}`}
              onClick={() => onSetZip(z.code)}
            >
              {z.city} ({z.code})
            </button>
          ))}
        </div>
      </div>

      {/* Festival Toggle */}
      <div className="dev-section">
        <h3>🎊 Festival Toggle</h3>
        <div className="dev-buttons">
          {festivals.map(f => (
            <button
              key={f}
              className="dev-btn"
              onClick={() => onSetFestival(f)}
            >
              {f.replace(/_/g, ' ')}
            </button>
          ))}
          <button className="dev-btn warning" onClick={() => onSetFestival(null)}>
            ❌ No Festival
          </button>
        </div>
      </div>

      {/* Time Warp */}
      <div className="dev-section">
        <h3>⏰ Time Warp (Intent Decay Demo)</h3>
        <div className="dev-buttons">
          <button className="dev-btn" onClick={() => onTimeWarp(24)}>+24 Hours</button>
          <button className="dev-btn" onClick={() => onTimeWarp(168)}>+7 Days</button>
          <button className="dev-btn" onClick={() => onTimeWarp(720)}>+30 Days</button>
        </div>
      </div>

      {/* Velocity Surge */}
      <div className="dev-section">
        <h3>📈 Velocity Surge</h3>
        <button className="dev-btn highlight" onClick={onVelocitySurge}>
          🚀 Simulate Local Velocity Surge
        </button>
      </div>

      {/* Log Output */}
      <div className="dev-section">
        <h3>📋 Engine Log</h3>
        <div className="dev-log">
          {devLog.length === 0 ? (
            <p className="log-empty">No actions yet. Use controls above.</p>
          ) : (
            devLog.map((entry, i) => (
              <div key={i} className="log-entry">{entry}</div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default DevPanel;
