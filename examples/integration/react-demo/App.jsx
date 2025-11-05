import React, { useState } from 'react';

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onFileChange = (e) => setFile(e.target.files?.[0] || null);

  async function callEndpoint(endpoint) {
    if (!file) {
      setError('Veuillez sélectionner un fichier (.pdf/.docx)');
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await fetch(`http://localhost:4000${endpoint}`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || JSON.stringify(data));
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h2>React ↔ Node Proxy ↔ FastAPI</h2>
      <p>Téléversez un CV (.pdf, .docx) et testez les endpoints.</p>
      <input type="file" onChange={onFileChange} accept=".pdf,.docx,.doc,.txt" />
      <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
        <button disabled={loading || !file} onClick={() => callEndpoint('/api/resume/analyze')}>Analyser</button>
        <button disabled={loading || !file} onClick={() => callEndpoint('/api/resume/rewrite')}>Réécrire</button>
      </div>
      {loading && <p>Chargement...</p>}
      {error && <pre style={{ color: 'crimson', background: '#fee', padding: 8 }}>{error}</pre>}
      {result && <pre style={{ background: '#f6f8fa', padding: 12 }}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
