import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRecommendations } from '../services/api';
import MovieCard from '../components/MovieCard';
import { MOODS } from '../constants/config';
import './RecommendationsScreen.css';

const RecommendationsScreen = () => {
  const navigate = useNavigate();
  const [selectedMood, setSelectedMood] = useState('веселое');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async (mood) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRecommendations(mood);
      if (data.success) {
        setRecommendations(data.recommendations || []);
      } else {
        setError(data.error || 'Ошибка получения рекомендаций');
      }
    } catch (err) {
      setError('Не удалось подключиться к серверу. Убедитесь, что сервер запущен.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations(selectedMood);
  }, [selectedMood]);

  const getCurrentMoodEmoji = () => {
    const mood = MOODS.find(m => m.id === selectedMood);
    return mood ? mood.emoji : '🎬';
  };

  return (
    <div className="recommendations-screen">
      <header className="rec-header">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Назад
        </button>
        <h1 className="rec-title">Выберите настроение</h1>
      </header>

      <div className="moods-container">
        {MOODS.map((mood) => (
          <button
            key={mood.id}
            className={`mood-button ${selectedMood === mood.id ? 'active' : ''}`}
            onClick={() => setSelectedMood(mood.id)}
          >
            <span className="mood-emoji">{mood.emoji}</span>
            <span className="mood-label">{mood.label}</span>
          </button>
        ))}
      </div>

      <div className="rec-content">
        {loading ? (
          <div className="centered">
            <div className="loader">🎬</div>
            <p>Подбираем фильмы...</p>
          </div>
        ) : error ? (
          <div className="centered">
            <div className="error-emoji">😕</div>
            <p>{error}</p>
            <button className="retry-button" onClick={() => fetchRecommendations(selectedMood)}>
              Повторить
            </button>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="centered">
            <div className="empty-emoji">🎬</div>
            <p>Рекомендации не найдены</p>
          </div>
        ) : (
          <>
            <div className="results-header">
              <h2>Рекомендации для вас</h2>
            </div>
            <div className="movies-list">
              {recommendations.map((movie, index) => (
                <MovieCard key={movie.id || index} movie={movie} index={index} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RecommendationsScreen;