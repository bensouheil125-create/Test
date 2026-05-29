import React from 'react';

const services = [
  { id: 'audio', title: 'ملخص صوتي', icon: '🎙️', className: 'audio' },
  { id: 'video', title: 'ملخص فيديو', icon: '🎬', className: 'video' },
  { id: 'presentation', title: 'عرض تقديمي', icon: '🖥️', className: 'presentation' },
  { id: 'flashcards', title: 'بطاقات تعليمية', icon: '🗂️', className: 'flashcards' },
  { id: 'quiz', title: 'اختبار', icon: '❓', className: 'quiz' },
  { id: 'infographic', title: 'إنفوغرافيك', icon: '📊', className: 'infographic' },
];

function StudioPage({ fileData, onServiceClick }) {
  return (
    <div>
      <div className="file-info">
        <h3>📄 {fileData.اسم_الملف}</h3>
        <p>
          عدد الصفحات: {fileData.معلومات?.عدد_الصفحات || '—'} |
          حجم النص: {fileData.طول_النص?.toLocaleString()} حرف
        </p>

        {fileData.معاينة && (
          <p style={{ marginTop: 8, fontSize: '0.8rem', color: '#666' }}>
            {fileData.معاينة.substring(0, 120)}...
          </p>
        )}
      </div>

      <p className="section-title">توليد محتوى جديد</p>

      <div className="services-grid">
        {services.map((service) => (
          <button
            key={service.id}
            className={`service-card ${service.className}`}
            onClick={() => onServiceClick(service)}
          >
            <div className="card-content">
              <span className="card-icon">{service.icon}</span>
              <span className="card-title">{service.title}</span>
            </div>
            <div className="arrow">←</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default StudioPage;
