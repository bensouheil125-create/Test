import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function SettingsPage() {
  const [provider, setProvider] = useState('openai');
  const [apiKey, setApiKey] = useState('');
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => { checkStatus(); }, []);


  const checkStatus = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/settings/api-key`);
      setStatus(res.data);
      setProvider(res.data.active_provider || 'openai');
    } catch (e) {
      setStatus(null);
    }
  };

  const saveKey = async () => {
    if (!apiKey.trim()) {
      setMessage('الرجاء إدخال مفتاح API');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      const res = await axios.post(`${API_URL}/api/settings/api-key`, {
        provider,
        key: apiKey.trim()
      });
      if (res.data.نجاح) {
        setMessage('✅ ' + res.data.رسالة);
        setApiKey('');
        checkStatus();
      }
    } catch (e) {
      setMessage('❌ ' + (e.response?.data?.خطأ || 'فشل في الحفظ'));
    } finally {
      setSaving(false);
    }
  };


  return (
    <div className="settings-page">
      <h2>⚙️ إعدادات الذكاء الاصطناعي</h2>

      {/* حالة الاتصال */}
      <div className="settings-section">
        <h3>حالة الذكاء الاصطناعي</h3>
        <p>
          OpenAI: {' '}
          <span className={`status-badge ${status?.openai_configured ? 'active' : 'inactive'}`}>
            {status?.openai_configured ? 'مفعل ✓' : 'غير مفعل'}
          </span>
        </p>
        <p>
          Google Gemini: {' '}
          <span className={`status-badge ${status?.gemini_configured ? 'active' : 'inactive'}`}>
            {status?.gemini_configured ? 'مفعل ✓' : 'غير مفعل'}
          </span>
        </p>
        <p style={{marginTop: 10, color: '#888', fontSize: '0.8rem'}}>
          المزود النشط: {status?.active_provider === 'gemini' ? 'Google Gemini' : 'OpenAI'}
        </p>
      </div>

      {/* إدخال المفتاح */}
      <div className="settings-section">
        <h3>🔑 إضافة مفتاح API</h3>
        <p>أدخل مفتاح API الخاص بك لتفعيل الذكاء الاصطناعي المتقدم</p>

        <div className="input-group">
          <label>اختر المزود:</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="openai">OpenAI (GPT-4o-mini)</option>
            <option value="gemini">Google Gemini</option>
          </select>
        </div>

        <div className="input-group" style={{marginTop: 12}}>
          <label>مفتاح API:</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={provider === 'openai' ? 'sk-...' : 'AIza...'}
          />
        </div>

        <button
          className="btn-primary"
          onClick={saveKey}
          disabled={saving}
          style={{marginTop: 15, width: '100%'}}
        >
          {saving ? 'جاري الحفظ...' : 'حفظ المفتاح'}
        </button>

        {message && (
          <p className={message.includes('✅') ? 'success-msg' : 'error-msg'}>
            {message}
          </p>
        )}
      </div>

      {/* معلومات */}
      <div className="settings-section">
        <h3>💡 ملاحظات</h3>
        <p>• بدون مفتاح API: يعمل التطبيق بخوارزميات أساسية</p>
        <p>• مع مفتاح API: تلخيص ذكي، أسئلة متقدمة، بطاقات أفضل</p>
        <p>• المفتاح يُحفظ في الجلسة فقط ولا يُخزن على الخادم</p>
        <p style={{marginTop: 8, fontSize: '0.8rem', color: '#666'}}>
          احصل على مفتاح OpenAI من: platform.openai.com<br/>
          احصل على مفتاح Gemini من: aistudio.google.com
        </p>
      </div>
    </div>
  );
}

export default SettingsPage;
