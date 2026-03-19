import axios from 'axios';
import { API_BASE_URL } from '../constants/config';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const getRecommendations = async (mood) => {
  const response = await api.get('/recommendations', { params: { mood } });
  return response.data;
};

export const getMoods = async () => {
  const response = await api.get('/moods');
  return response.data;
};

export default api;