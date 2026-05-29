import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ResultPage({ resultData, onBack, fileData }) {
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showAnswers, setShowAnswers] = useState({});
  const [currentSlide, setCurrentSlide] = useState(0);

  const fileId = resultData.fileId;
  const service = resultData.service;

  useEffect(() => { fetchContent(); }, []);


  const fetchContent = async () => {
    setLoading(true);
    setError(null);
    try {
      let response;
      switch (service.id) {
        case 'audio':
          response = await axios.get(`${API_URL}/api/audio/${fileId}`, { responseType: 'blob' });
          setContent({ type: 'audio', url: URL.createObjectURL(response.data) });
          break;
        case 'video':
          response = await axios.get(`${API_URL}/api/video/${fileId}`, { responseType: 'blob' });
          const ct = response.headers['content-type'];
          if (ct && ct.includes('video')) {
            setContent({ type: 'video', url: URL.createObjectURL(response.data) });
          } else {
            setContent({ type: 'audio', url: URL.createObjectURL(response.data),
              note: 'تم إنشاء الملخص الصوتي. لإنشاء فيديو كامل يلزم ffmpeg.' });
          }
          break;
        case 'presentation':
          response = await axios.get(`${API_URL}/api/presentation/${fileId}`);
          setContent({ type: 'presentation', slides: response.data.شرائح });
          break;
        case 'flashcards':
          response = await axios.get(`${API_URL}/api/flashcards/${fileId}`);
          setContent({ type: 'flashcards', cards: response.data.بطاقات });
          break;
        case 'quiz':
          response = await axios.get(`${API_URL}/api/quiz/${fileId}`);
          setContent({ type: 'quiz', questions: response.data.اختبار });
          break;
        case 'infographic':
          response = await axios.get(`${API_URL}/api/infographic/${fileId}`, { responseType: 'blob' });
          setContent({ type: 'image', url: URL.createObjectURL(response.data) });
          break;
        default:
          setError('خدمة غير معروفة');
      }
    } catch (err) {
      setError(err.response?.data?.خطأ || 'حدث خطأ أثناء التوليد');
    } finally {
      setLoading(false);
    }
  };


  const toggleFlashcard = (i) => setShowAnswers({...showAnswers, [i]: !showAnswers[i]});
  const handleOption = (qi, opt) => {
    setSelectedAnswers({...selectedAnswers, [qi]: opt});
    setShowAnswers({...showAnswers, [qi]: true});
  };

  if (loading) return (
    <div className="loading">
      <div className="spinner"></div>
      <p>جاري توليد {service.title}...</p>
    </div>
  );

  if (error) return (
    <div className="result-page">
      <div className="result-content" style={{textAlign:'center'}}>
        <p style={{color:'#f44336',fontSize:'1.1rem'}}>⚠️ {error}</p>
        <button className="btn-primary" onClick={fetchContent} style={{marginTop:15}}>
          إعادة المحاولة
        </button>
      </div>
    </div>
  );

  return (
    <div className="result-page">
      {content?.type === 'audio' && (
        <div className="result-content">
          <h2>🎙️ الملخص الصوتي</h2>
          {content.note && <p style={{color:'#ffa726',marginBottom:10}}>{content.note}</p>}
          <audio controls className="audio-player" src={content.url} />
          <a href={content.url} download="ملخص_صوتي.mp3" className="btn-primary"
            style={{display:'inline-block',marginTop:15,textDecoration:'none'}}>
            تحميل الملف
          </a>
        </div>
      )}


      {content?.type === 'video' && (
        <div className="result-content">
          <h2>🎬 الفيديو التعليمي</h2>
          <video controls style={{width:'100%',borderRadius:8,marginTop:10}}>
            <source src={content.url} type="video/mp4" />
          </video>
          <a href={content.url} download="فيديو.mp4" className="btn-primary"
            style={{display:'inline-block',marginTop:15,textDecoration:'none'}}>
            تحميل الفيديو
          </a>
        </div>
      )}

      {content?.type === 'presentation' && (
        <div>
          <h2>🖥️ العرض التقديمي</h2>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:15}}>
            <button className="btn-primary" onClick={()=>setCurrentSlide(Math.max(0,currentSlide-1))}
              disabled={currentSlide===0} style={{padding:'8px 16px',fontSize:'0.9rem'}}>السابق</button>
            <span style={{color:'#aaa'}}>{currentSlide+1}/{content.slides.length}</span>
            <button className="btn-primary" onClick={()=>setCurrentSlide(Math.min(content.slides.length-1,currentSlide+1))}
              disabled={currentSlide===content.slides.length-1} style={{padding:'8px 16px',fontSize:'0.9rem'}}>التالي</button>
          </div>
          {content.slides[currentSlide] && (
            <div className="slide">
              <div className="slide-title">{content.slides[currentSlide].عنوان}</div>
              <div className="slide-content">
                {content.slides[currentSlide].نوع === 'نقاط' ? (
                  <ul>{Array.isArray(content.slides[currentSlide].محتوى) &&
                    content.slides[currentSlide].محتوى.map((p,i)=><li key={i}>{p}</li>)}</ul>
                ) : (<p>{content.slides[currentSlide].محتوى}</p>)}
              </div>
            </div>
          )}
        </div>
      )}


      {content?.type === 'flashcards' && (
        <div>
          <h2>🗂️ البطاقات التعليمية ({content.cards.length})</h2>
          {content.cards.map((card, i) => (
            <div key={i} className="flashcard" onClick={()=>toggleFlashcard(i)}>
              <div className="question">❓ {card.سؤال}</div>
              {showAnswers[i] ? (
                <div className="answer">💡 {card.جواب}</div>
              ) : (
                <p className="tap-hint">انقر لإظهار الجواب</p>
              )}
            </div>
          ))}
        </div>
      )}

      {content?.type === 'quiz' && (
        <div>
          <h2>❓ الاختبار ({content.questions.length} أسئلة)</h2>
          {content.questions.map((q, qi) => (
            <div key={qi} className="quiz-question">
              <div className="q-text">{qi+1}. {q.سؤال}</div>
              <div className="options">
                {q.الخيارات?.map((opt, oi) => (
                  <div key={oi}
                    className={`option ${showAnswers[qi]
                      ? opt===q.الإجابة_الصحيحة ? 'correct'
                      : selectedAnswers[qi]===opt ? 'wrong' : ''
                      : ''}`}
                    onClick={()=>handleOption(qi, opt)}>{opt}</div>
                ))}
              </div>
              {showAnswers[qi] && q.شرح && (
                <p style={{marginTop:10,color:'#4caf50',fontSize:'0.85rem'}}>
                  ✅ {q.شرح.substring(0, 120)}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {content?.type === 'image' && (
        <div className="result-content">
          <h2>📊 الإنفوغرافيك</h2>
          <img src={content.url} alt="إنفوغرافيك"
            style={{width:'100%',borderRadius:8,marginTop:10}} />
          <a href={content.url} download="إنفوغرافيك.png" className="btn-primary"
            style={{display:'inline-block',marginTop:15,textDecoration:'none'}}>
            تحميل الصورة
          </a>
        </div>
      )}
    </div>
  );
}

export default ResultPage;
