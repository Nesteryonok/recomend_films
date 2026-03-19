import React from 'react';
import './MovieCard.css';

const MovieCard = ({ movie, index }) => {
  return (
    <div className="movie-card-compact">
      <div className="compact-number">{index + 1}</div>
      <div className="compact-content">
        <h3 className="compact-title">{movie.name || movie.title}</h3>
        <div className="compact-meta">
          <span className="compact-genres">{movie.genres || 'Жанр не указан'}</span>
          {movie.emotions && (
            <span className="compact-emotion"> {movie.emotions}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MovieCard;