import { api, setToken } from './api';
export async function register(email: string, password: string, tenant: string){
  const { data } = await api.post('/auth/register', { email, password, tenant_name: tenant });
  setToken(data.access_token);
}
export async function login(email: string, password: string){
  const { data } = await api.post('/auth/login', { email, password });
  setToken(data.access_token);
}
