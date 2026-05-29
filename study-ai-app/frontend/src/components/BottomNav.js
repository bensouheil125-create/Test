import React from 'react';

function BottomNav({ activeTab, onTabChange }) {
  return (
    <div className="bottom-nav">
      <button
        className={`nav-item ${activeTab === 'sources' ? 'active' : ''}`}
        onClick={() => onTabChange('sources')}
      >
        <span className="nav-icon">📁</span>
        <span className="nav-label">المصادر</span>
      </button>
      <button
        className={`nav-item ${activeTab === 'studio' ? 'active' : ''}`}
        onClick={() => onTabChange('studio')}
      >
        <span className="nav-icon">🎨</span>
        <span className="nav-label">الاستوديو</span>
      </button>
      <button
        className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
        onClick={() => onTabChange('settings')}
      >
        <span className="nav-icon">⚙️</span>
        <span className="nav-label">الإعدادات</span>
      </button>
    </div>
  );
}

export default BottomNav;
