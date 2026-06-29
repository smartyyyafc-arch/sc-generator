import React, { useState } from 'react';

export default function ProxyManager({
  proxies,
  selectedProxy,
  onSelectProxy,
  onAddProxy,
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [proxyForm, setProxyForm] = useState({
    url: '',
    type: 'http',
  });

  const handleAddProxy = async () => {
    if (!proxyForm.url) {
      alert('Please enter a proxy URL');
      return;
    }

    const id = await onAddProxy(proxyForm.url, proxyForm.type);
    if (id) {
      setProxyForm({ url: '', type: 'http' });
      setShowAddForm(false);
    }
  };

  return (
    <div>
      <div className="form-group">
        <label>Use Proxy:</label>
        <select
          value={selectedProxy || ''}
          onChange={(e) => onSelectProxy(e.target.value || null)}
        >
          <option value="">None</option>
          {proxies.map((px) => (
            <option key={px.id} value={px.id}>
              {px.url} ({px.type})
            </option>
          ))}
        </select>
      </div>

      <button
        className="btn-secondary"
        onClick={() => setShowAddForm(!showAddForm)}
        style={{ width: '100%', marginBottom: '1rem' }}
      >
        {showAddForm ? '✕ Cancel' : '➕ Add Proxy'}
      </button>

      {showAddForm && (
        <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: 'rgba(0, 212, 255, 0.05)', borderRadius: '6px' }}>
          <div className="form-group">
            <label>Proxy URL:</label>
            <input
              type="text"
              value={proxyForm.url}
              onChange={(e) => setProxyForm({ ...proxyForm, url: e.target.value })}
              placeholder="e.g., http://proxy.example.com:8080"
            />
          </div>
          <div className="form-group">
            <label>Type:</label>
            <select
              value={proxyForm.type}
              onChange={(e) => setProxyForm({ ...proxyForm, type: e.target.value })}
            >
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
              <option value="socks5">SOCKS5</option>
            </select>
          </div>
          <button
            className="btn-primary"
            onClick={handleAddProxy}
            style={{ width: '100%' }}
          >
            Add Proxy
          </button>
        </div>
      )}

      <div style={{ fontSize: '0.85rem', color: '#a0a0a0' }}>
        <p>
          🌐 <strong>Proxies help:</strong> Modify fingerprints and evade
          detection by spoofing network signatures.
        </p>
      </div>
    </div>
  );
}
