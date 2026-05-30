import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MoodSelectorScreen.css';

const MoodSelectorScreen = () => {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [moodResult, setMoodResult] = useState(null); 
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    setIsCameraActive(false);
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      setError("Нет доступа к камере");
    }
  };

  const analyzeEmotion = async () => {
    if (!isCameraActive || !videoRef.current) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext('2d').drawImage(videoRef.current, 0, 0);
      
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));
      
      const formData = new FormData();
      formData.append('file', blob, 'shot.jpg');

      const response = await fetch('http://localhost:5555/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setMoodResult(data.dominant_mood); 
      }

    } catch (err) {
      setError("Ошибка соединения с сервером");
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = () => {
    if (moodResult) {
      stopCamera();
      navigate(`/recommendations?mood=${moodResult.id}`);
    }
  };

  return (
    <div className="mood-selector-screen">
      <header className="mood-header">
        <button className="back-button" onClick={() => { stopCamera(); navigate(-1); }}>← Назад</button>
        <h1>Подбор по настроению</h1>
        <p>Камера определит, какое настроение у вас сейчас</p>
      </header>

      <main className="mood-content">
        <div className="camera-container">
          {!isCameraActive && !error && (
            <div className="camera-placeholder">
              <div className="placeholder-icon"></div>
              <button className="start-cam-btn" onClick={startCamera}>Включить камеру</button>
            </div>
          )}
          
          {error && <div className="error-message">{error}</div>}

          <video ref={videoRef} autoPlay playsInline muted className={`video-feed ${isCameraActive ? 'active' : ''}`} />

          {isCameraActive && !moodResult && (
            <div className="camera-controls">
              <button className="analyze-btn" onClick={analyzeEmotion} disabled={isLoading}>
                {isLoading ? 'Анализ...' : 'Определить настроение'}
              </button>
            </div>
          )}
        </div>

        {moodResult && (
          <div className="result-card fade-in">
            <h2>Вам подходит:</h2>
            <div className="mood-display">
              <span className="mood-emoji">{moodResult.emoji}</span>
              <span className="mood-label">{moodResult.label}</span>
            </div>
            
            <div className="action-buttons">
              <button className="confirm-btn" onClick={handleConfirm}>
                Показать фильмы ({moodResult.label})
              </button>
              <button className="retry-btn" onClick={() => setMoodResult(null)}>
                Попробовать снова
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default MoodSelectorScreen;