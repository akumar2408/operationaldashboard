import axios from 'axios';
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000' });
export function setToken(token?: string){
  if(token){ api.defaults.headers.common['Authorization'] = `Bearer ${token}`; localStorage.setItem('token', token); }
  else { delete api.defaults.headers.common['Authorization']; localStorage.removeItem('token'); }
}
export function loadToken(){ const t = localStorage.getItem('token'); if(t) setToken(t); }
