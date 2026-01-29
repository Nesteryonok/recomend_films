import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [moods, setMoods] = useState([]);
  const [selectedMood, setSelectedMood] = useState('веселое');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка списка настроений при старте
  useEffect(() => {
    fetchMoods();
  }, []);

  // Загрузка рекомендаций при изменении настроения
  useEffect(() => {
    if (selectedMood) {
      fetchRecommendations(selectedMood);
    }
  }, [selectedMood]);

  const fetchMoods = async () => {
    try {
      const response = await fetch(`${API_URL}/moods`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // Заменяем "Все фильмы" на "Лучшее" для кнопки
      const processedMoods = data.moods.map(mood => 
        mood.id === 'все' ? { ...mood, label: 'Лучшее' } : mood
      );
      
      setMoods(processedMoods);
    } catch (error) {
      console.error('Ошибка загрузки настроений:', error);
      setError('Не удалось загрузить список настроений');
    }
  };

  const fetchRecommendations = async (mood) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/recommendations?mood=${mood}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      if (data.success) {
        setItems(data.recommendations);
      } else {
        setError(data.error || 'Неизвестная ошибка');
      }
    } catch (error) {
      console.error('Ошибка загрузки рекомендаций:', error);
      setError('Не удалось загрузить рекомендации. Проверьте, запущен ли сервер.');
    } finally {
      setLoading(false);
    }
  };

  const handleMoodSelect = (moodId) => {
    setSelectedMood(moodId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="App">
      <div className="header">
        <h1>🎬 КиноНавигатор</h1>
        <p>Рекомендации фильмов на основе вашего настроения</p>
      </div>

      <div className="mood-selector">
        <h2>🎭 Выберите настроение</h2>
        <div className="mood-buttons">
          {moods.map((mood) => (
            <button
              key={mood.id}
              className={`mood-button ${selectedMood === mood.id ? 'selected' : ''}`}
              onClick={() => handleMoodSelect(mood.id)}
            >
              <span className="emoji">{mood.emoji}</span>
              <span className="label">{mood.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="recommendations-section">
        <h2>
          {selectedMood === 'веселое' && '😄 Весёлые фильмы'}
          {selectedMood === 'эмоциональное' && '😢 Эмоциональные фильмы'}
          {selectedMood === 'романтическое' && '❤️ Романтические фильмы'}
          {selectedMood === 'страшное' && '😱 Страшные фильмы'}
          {selectedMood === 'динамичное' && '⚡ Динамичные фильмы'}
          {selectedMood === 'лёгкое' && '😌 Лёгкие фильмы'}
          {selectedMood === 'все' && '🎬 Топ 10 фильмов'}
        </h2>

        {error && (
          <div className="error">
            <h3>⚠️ Ошибка</h3>
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Загрузка рекомендаций...</p>
          </div>
        ) : items.length > 0 ? (
          <div className="movies-table">
            <table>
              <thead>
                <tr>
                  <th width="5%">№</th>
                  <th width="60%">Название фильма</th>
                  <th width="35%">Жанры</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.name}</td>
                    <td>
                      {/* Отображаем НАСТОЯЩИЕ жанры из колонки genres */}
                      {item.genres && item.genres.split('|').map((genre, idx) => (
                        <span key={idx} style={{
                          display: 'inline-block',
                          background: 'rgba(255, 255, 255, 0.15)',
                          padding: '2px 8px',
                          borderRadius: '10px',
                          fontSize: '0.85rem',
                          marginRight: '4px',
                          marginBottom: '4px',
                          color: '#4ecdc4'
                        }}>
                          {genre}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-results">
            <h3>📭 Нет рекомендаций</h3>
            <p>Попробуйте выбрать другое настроение</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;