import { useEffect, useState } from 'react';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import SalesUploader from './components/SalesUploader';
import { loadToken } from './api';
import Nav from './components/Nav';
import { Outlet } from 'react-router-dom'


export default function App(){
  const [authed, setAuthed] = useState(false);
  useEffect(()=>{ loadToken(); if(localStorage.getItem('token')) setAuthed(true); },[]);

  if(!authed) return <LoginForm onAuthed={()=>setAuthed(true)} />;
  return (
    <div>
      <Nav />
      <Dashboard />
      <SalesUploader />
    </div>
  );
}
