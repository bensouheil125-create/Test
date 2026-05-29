import React, { useState, useCallback } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function UploadPage({ onFileUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);


  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) uploadFile(files[0]);
  }, []);

  const handleFileSelect = useCallback((e) => {
    const files = e.target.files;
    if (files.length > 0) uploadFile(files[0]);
  }, []);

  const uploadFile = async (file) => {
    setIsUploading(true);
    setUploadProgress(0);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          setUploadProgress(Math.round((e.loaded * 100) / e.total));
        }
      });
      if (response.data.نجاح) {
        onFileUploaded(response.data);
      } else {
        alert(response.data.خطأ || 'حدث خطأ');
      }
    } catch (error) {
      alert(error.response?.data?.خطأ || 'فشل في رفع الملف');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };


  return (
    <div>
      <div
        className={`upload-zone ${isDragging ? 'active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          type="file" id="file-input"
          accept=".pdf,.txt,.docx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        {isUploading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>جاري رفع الملف... {uploadProgress}%</p>
          </div>
        ) : (
          <>
            <div className="icon">📚</div>
            <p>اسحب الملف هنا أو انقر للاختيار</p>
            <p className="supported">PDF, TXT, DOCX</p>
          </>
        )}
      </div>
      <div className="file-info">
        <h3>📖 كيف يعمل التطبيق؟</h3>
        <p>
          ١. ارفع كتاباً أو ملف PDF<br/>
          ٢. سيتم استخراج النص تلقائياً<br/>
          ٣. اختر الخدمة (ملخص صوتي، فيديو، بطاقات...)<br/>
          ٤. احصل على محتوى تعليمي بالعربية الفصحى
        </p>
      </div>
    </div>
  );
}

export default UploadPage;
