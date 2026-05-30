import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomeScreen from './screens/HomeScreen';
import RecommendationsScreen from './screens/RecommendationsScreen';
import MoodSelectorScreen from './screens/MoodSelectorScreen';

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomeScreen />} />
        <Route path="/recommendations" element={<RecommendationsScreen />} />
        <Route path="/mood-selector" element={<MoodSelectorScreen />} />
      </Routes>
    </div>
  );
}

export default App;