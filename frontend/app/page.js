'use client';

import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';

export default function HomePage() {
  const [username, setUsername] = useState('alice');
  const [query, setQuery] = useState('Summarize operations rollback thresholds');
  const [token, setToken] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const login = async () => {
    setError('');
    const resp = await fetch(`${API}/auth/token?username=${encodeURIComponent(username)}`, { method: 'POST' });
    if (!resp.ok) return setError('Authentication failed');
    const data = await resp.json();
    setToken(data.access_token);
  };

  const ask = async () => {
    setError('');
    const resp = await fetch(`${API}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ query }),
    });
    const data = await resp.json();
    if (!resp.ok) return setError(data.detail || 'Query failed');
    setResult(data);
  };

  return (
    <main>
      <h1>Ragverse Enterprise RAG Console</h1>
      <p>RBAC-first retrieval, hybrid search, and explainable responses.</p>

      <section>
        <h2>1) Authenticate</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="alice / bob / eve" />
        <button onClick={login} style={{ marginLeft: 8 }}>Get JWT</button>
      </section>

      <section style={{ marginTop: 16 }}>
        <h2>2) Query</h2>
        <textarea rows={4} style={{ width: '100%' }} value={query} onChange={(e) => setQuery(e.target.value)} />
        <button disabled={!token} onClick={ask}>Run Query</button>
      </section>

      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {result && (
        <section style={{ marginTop: 16 }}>
          <h2>Answer</h2>
          <pre>{result.answer}</pre>
          <p><strong>Confidence:</strong> {result.confidence}</p>
          <p><strong>Citations:</strong> {result.citations.join(', ')}</p>
          <h3>Source Attribution</h3>
          <pre>{JSON.stringify(result.source_attribution, null, 2)}</pre>
          <h3>Retrieval Trace</h3>
          <pre>{JSON.stringify(result.retrieval_trace, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}
