import { useState } from 'react'
import { api } from '../api'

export default function S3Uploader(){
  const [file, setFile] = useState<File|null>(null)
  const [msg, setMsg] = useState('')

  async function upload() {
    if(!file) return
    // 1) ask API for presigned POST
    const { data: presign } = await api.get('/sales/presign-upload', { params: { filename: file.name } })
    // 2) POST the file directly to S3
    const fd = new FormData()
    Object.entries(presign.fields).forEach(([k,v]) => fd.append(k, String(v)))
    fd.append('Content-Type','text/csv')
    fd.append('file', file)
    await fetch(presign.url, { method:'POST', body: fd })
    // 3) tell API to ingest that key
    await api.post('/sales/ingest-s3', null, { params: { key: presign.fields.key } })
    setMsg(`Uploaded & ingested ${file.name}`)
  }

  return (
    <div className="p-4 rounded-2xl border border-black/10 dark:border-white/10 space-y-3">
      <h3 className="text-lg font-semibold">Upload Sales CSV (S3)</h3>
      <input type="file" accept=".csv" onChange={e=>setFile(e.target.files?.[0]||null)} />
      <button className="px-3 py-2 rounded-lg bg-black text-white dark:bg-white dark:text-black disabled:opacity-40"
              disabled={!file} onClick={upload}>Upload</button>
      {msg && <p className="text-emerald-600 dark:text-emerald-400">{msg}</p>}
    </div>
  )
}
