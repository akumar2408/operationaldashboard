import { useState } from 'react';
import { login, register } from '../auth';

type Props = { onAuthed: () => void };

export default function LoginForm({ onAuthed }: Props){
  const [mode, setMode] = useState<'login'|'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tenant, setTenant] = useState('My Shop');
  const [err, setErr] = useState('');

  async function submit(){
    setErr('');
    try{
      if(mode==='login') await login(email, password);
      else await register(email, password, tenant);
      onAuthed();
    }catch(e:any){
      setErr(e?.response?.data?.detail || 'Error');
    }
  }

  return (
    <div style={{maxWidth: 420, margin: '3rem auto'}}>
      <h2>{mode==='login'?'Welcome back':'Create your account'}</h2>
      <input placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      {mode==='register' && (
        <input placeholder="tenant / business name" value={tenant} onChange={e=>setTenant(e.target.value)} />
      )}
      <button onClick={submit}>{mode==='login'?'Login':'Register'}</button>
      <div style={{marginTop:8}}>
        <a onClick={()=>setMode(mode==='login'?'register':'login')}>
          {mode==='login'? 'Create an account' : 'Already have an account? Login'}
        </a>
      </div>
      {err && <p style={{color:'crimson'}}>{err}</p>}
    </div>
  );
}
