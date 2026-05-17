'use client';

import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';

export default function HomePage() {
  const [username, setUsername] = useState('alice');
  const [query, setQuery] = useState('Summarize Q2 revenue risks and budget variance.');
  const [token, setToken] = useState('');
  const [role, setRole] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const demoUsers = [
    { label: 'Alice (HR Manager)', value: 'alice' },
    { label: 'Bob (Engineering Manager)', value: 'bob' },
    { label: 'Carol (Finance Manager)', value: 'carol' },
    { label: 'Diana (Admin)', value: 'diana' },
  ];

  const demoQueries = [
    {
      label: 'Authorized: Finance',
      value: 'Summarize Q2 revenue risks and budget variance.',
    },
    {
      label: 'Unauthorized: HR Salary',
      value: 'Show employee salary bands for Q2.',
    },
    {
      label: 'Cross-source',
      value: 'Were failed admin logins associated with payroll updates?',
    },
  ];

  const login = async () => {
    setError('');
    const resp = await fetch(`${API}/auth/token?username=${encodeURIComponent(username)}`, { method: 'POST' });
    if (!resp.ok) return setError('Authentication failed');
    const data = await resp.json();
    setToken(data.access_token);
    setRole(data.role || '');
  };

  const ask = async () => {
    setError('');
    const resp = await fetch(`${API}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ query }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      const detail = data.error ? `${data.error}: ${data.reason}` : data.detail || 'Query failed';
      const blocked = data.blocked_sources?.length ? ` (Blocked: ${data.blocked_sources.join(', ')})` : '';
      setResult(null);
      return setError(`${detail}${blocked}`);
    }
    setResult(data);
  };

  return (
    <main>
      <h1>Ragverse Enterprise RAG Console</h1>
      <p>RBAC-first retrieval, hybrid search, and explainable responses.</p>

      <section>
        <h2>1) Authenticate</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="alice / bob / carol" />
        <button onClick={login} style={{ marginLeft: 8 }}>Get JWT</button>
        {role && <span style={{ marginLeft: 12 }}>Role: <strong>{role}</strong></span>}
        <div style={{ marginTop: 8 }}>
          {demoUsers.map((user) => (
            <button
              key={user.value}
              onClick={() => setUsername(user.value)}
              style={{ marginRight: 8, marginTop: 4 }}
            >
              {user.label}
            </button>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 16 }}>
        <h2>2) Query</h2>
        <textarea rows={4} style={{ width: '100%' }} value={query} onChange={(e) => setQuery(e.target.value)} />
        <button disabled={!token} onClick={ask}>Run Query</button>
        <div style={{ marginTop: 8 }}>
          {demoQueries.map((demo) => (
            <button
              key={demo.label}
              onClick={() => setQuery(demo.value)}
              style={{ marginRight: 8, marginTop: 4 }}
            >
              {demo.label}
            </button>
          ))}
        </div>
      </section>

      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {result && (
        <section style={{ marginTop: 16 }}>
          <h2>Answer</h2>
          <pre>{result.answer}</pre>
          <p><strong>Confidence:</strong> {result.confidence}</p>
          <p><strong>Cross-source:</strong> {result.cross_source ? 'Yes' : 'No'}</p>
          <p><strong>Citations:</strong> {result.citations.join(', ')}</p>
          <p><strong>Blocked Sources:</strong> {result.blocked_sources?.join(', ') || 'None'}</p>
          <h3>Source Attribution</h3>
          <pre>{JSON.stringify(result.source_attribution, null, 2)}</pre>
          <h3>Governance</h3>
          <pre>{JSON.stringify(result.governance, null, 2)}</pre>
          <h3>Retrieval Trace</h3>
          <pre>{JSON.stringify(result.retrieval_trace, null, 2)}</pre>
          <h3>Retrieved Chunks</h3>
          <div>
            {result.retrieved_chunks.map((chunk) => (
              <div key={chunk.chunk_id} style={{ marginBottom: 12, padding: 8, border: '1px solid #ddd' }}>
                <strong>{chunk.document_id}</strong> ({chunk.source}) — score {chunk.score.toFixed(3)}
                <pre style={{ whiteSpace: 'pre-wrap' }}>{chunk.content}</pre>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
