import { useState } from 'react';
import { api } from '../api';

export default function SalesUploader(){
  const [file, setFile] = useState<File|null>(null);
  const [msg, setMsg] = useState('');

  async function upload(){
    if(!file) return;
    const fd = new FormData();
    fd.append('file', file);
    const { data } = await api.post('/sales/upload-csv', fd);
    setMsg(`Uploaded ${data.rows} rows`);
  }

  return (
    <div style={{padding: 24}}>
      <h3>Upload Sales CSV</h3>
      <input type="file" accept=".csv" onChange={e=>setFile(e.target.files?.[0]||null)} />
      <button onClick={upload} disabled={!file}>Upload</button>
      {msg && <p>{msg}</p>}
    </div>
  );
}
