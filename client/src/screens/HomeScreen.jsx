import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomeScreen.css';

const HomeScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="home-screen">
      <header className="header">
        <div className="logo-container">
          <div className="logo-icon">🎬</div>
          <div>
            <h1 className="logo-text">FilmMood</h1>
            <p className="logo-subtitle">Помогаем выбрать фильм по настроению</p>
          </div>
        </div>
      </header>

      <section className="hero">
        <div className="hero-overlay">
          <h2 className="hero-title">
            Не знаете, что посмотреть?<br />
            Найдите фильм под свое настроение
          </h2>
          <p className="hero-subtitle">
            Простой способ найти кино, которое идеально совпадет с вашим настроением.
            Просто выберите эмоцию и получите рекомендацию.
          </p>
          <div className="hero-buttons">
            <button className="hero-button" onClick={() => navigate('/recommendations')}>
              Подобрать фильм
            </button>
            <button className="hero-button" onClick={() => navigate('/mood-selector')}>
              Определить эмоцию
            </button>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <h2 className="section-title">Как это работает?</h2>

        <div className="steps-container">
          <div className="step">
            <div className="film-frame">
              <div className="film-holes-top">
                {[...Array(8)].map((_, i) => <div key={`t1-${i}`} className="film-hole" />)}
              </div>
              <div className="film-content">
                <div className="number-circle"><span>3</span></div>
              </div>
              <div className="film-holes-bottom">
                {[...Array(8)].map((_, i) => <div key={`b1-${i}`} className="film-hole" />)}
              </div>
            </div>
            <h3 className="step-title">Выберите настроение</h3>
            <p className="step-description">Отметьте, чего просит душа — веселья, драмы, романтики?</p>
          </div>

          <div className="step">
            <div className="film-frame">
              <div className="film-holes-top">
                {[...Array(8)].map((_, i) => <div key={`t2-${i}`} className="film-hole" />)}
              </div>
              <div className="film-content">
                <div className="number-circle"><span>2</span></div>
              </div>
              <div className="film-holes-bottom">
                {[...Array(8)].map((_, i) => <div key={`b2-${i}`} className="film-hole" />)}
              </div>
            </div>
            <h3 className="step-title">Нажмите кнопку</h3>
            <p className="step-description">Всего один клик на странице нашей системы рекомендаций</p>
          </div>

          <div className="step">
            <div className="film-frame">
              <div className="film-holes-top">
                {[...Array(8)].map((_, i) => <div key={`t3-${i}`} className="film-hole" />)}
              </div>
              <div className="film-content">
                <div className="number-circle"><span>1</span></div>
              </div>
              <div className="film-holes-bottom">
                {[...Array(8)].map((_, i) => <div key={`b3-${i}`} className="film-hole" />)}
              </div>
            </div>
            <h3 className="step-title">Получите рекомендации</h3>
            <p className="step-description">Мгновенно получите список фильмов, которые вам понравятся</p>
          </div>
        </div>
      </section>

      <section className="features">
        <h2 className="features-title">Ваш идеальный киновечер начинается здесь</h2>
        <p className="features-text">
          Не можете выбрать фильм?  Мы здесь, чтобы помочь! Наша система подберет фильм именно под ваше текущее настроение.
        </p>
      </section>

      <section className="cta-section">
        <div className="cta-container">
          <button className="cta-button primary" onClick={() => navigate('/recommendations')}>
            <span>Начать подбор</span>
          </button>

          <button className="cta-button secondary" onClick={() => navigate('/mood-selector')}>
            <span>Определить эмоцию</span>
          </button>
        </div>
      </section>

      <footer className="footer">
        <p>© 2026 FilmMood. Приятного просмотра</p>
      </footer>
    </div>
  );
};

export default HomeScreen;