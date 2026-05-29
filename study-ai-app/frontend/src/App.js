import React, { useState, useCallback } from 'react';
import UploadPage from './pages/UploadPage';
import StudioPage from './pages/StudioPage';
import ResultPage from './pages/ResultPage';
import SettingsPage from './pages/SettingsPage';
import BottomNav from './components/BottomNav';

function App() {
  const [currentPage, setCurrentPage] = useState('upload');
  const [fileData, setFileData] = useState(null);
  const [resultData, setResultData] = useState(null);
  const [activeTab, setActiveTab] = useState('sources');

  const handleFileUploaded = useCallback((data) => {
    setFileData(data);
    setCurrentPage('studio');
    setActiveTab('studio');
  }, []);

  const handleServiceClick = useCallback((service) => {
    setResultData({ service, fileId: fileData?.معرف_الملف });
    setCurrentPage('result');
  }, [fileData]);

  const handleBack = useCallback(() => {
    if (currentPage === 'result') {
      setCurrentPage('studio');
    } else if (currentPage === 'studio') {
      setCurrentPage('upload');
      setActiveTab('sources');
    } else if (currentPage === 'settings') {
      if (fileData) {
        setCurrentPage('studio');
        setActiveTab('studio');
      } else {
        setCurrentPage('upload');
        setActiveTab('sources');
      }
    }
  }, [currentPage, fileData]);

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
    if (tab === 'sources') {
      setCurrentPage('upload');
    } else if (tab === 'studio' && fileData) {
      setCurrentPage('studio');
    } else if (tab === 'settings') {
      setCurrentPage('settings');
    }
  }, [fileData]);

  const getPageTitle = () => {
    switch (currentPage) {
      case 'upload': return 'دراستي الذكية';
      case 'studio': return fileData?.اسم_الملف || 'الاستوديو';
      case 'result': return resultData?.service?.title || 'النتيجة';
      case 'settings': return 'الإعدادات';
      default: return 'دراستي الذكية';
    }
  };

  return (
    <div className="app">
      {/* شريط التنقل العلوي */}
      <nav className="navbar">
        {currentPage !== 'upload' ? (
          <button className="back-btn" onClick={handleBack}>→</button>
        ) : <span style={{ width: 35 }}></span>}

        <h1>{getPageTitle()}</h1>

        <button 
          className="settings-btn" 
          onClick={() => { setCurrentPage('settings'); setActiveTab('settings'); }}
          title="الإعدادات"
        >
          ⚙️
        </button>
      </nav>

      {/* المحتوى الرئيسي */}
      <div className="main-content">
        {currentPage === 'upload' && (
          <UploadPage onFileUploaded={handleFileUploaded} />
        )}
        {currentPage === 'studio' && fileData && (
          <StudioPage fileData={fileData} onServiceClick={handleServiceClick} />
        )}
        {currentPage === 'result' && resultData && (
          <ResultPage resultData={resultData} onBack={handleBack} fileData={fileData} />
        )}
        {currentPage === 'settings' && (
          <SettingsPage />
        )}
      </div>

      {/* شريط التنقل السفلي */}
      <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />
    </div>
  );
}

export default App;
