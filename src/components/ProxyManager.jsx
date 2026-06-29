import React, { useState } from 'react';

export default function ProxyManager({
  proxies,
  selectedProxy,
  onSelectProxy,
  onAddProxy,
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
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
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Proxy Configuration</span>
          <button
            className="btn-secondary"
            onClick={() => setShowInfo(!showInfo)}
            style={{
              padding: '0.4rem 0.8rem',
              fontSize: '0.85rem',
              backgroundColor: 'rgba(0, 212, 255, 0.1)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
            }}
          >
            {showInfo ? 'Hide Info' : 'ℹ️ Info'}
          </button>
        </label>

        {showInfo && (
          <div
            style={{
              marginBottom: '1rem',
              padding: '1rem',
              backgroundColor: 'rgba(0, 212, 255, 0.08)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: '6px',
              fontSize: '0.85rem',
              color: '#a0a0a0',
              lineHeight: '1.6',
            }}
          >
            <p style={{ marginTop: 0 }}>
              <strong>🌐 What are Proxies?</strong>
            </p>
            <p>
              Proxies modify network signatures and fingerprints, making your payload appear to come from
              different sources and evading IP-based detection.
            </p>
            <p>
              <strong>When to use:</strong>
            </p>
            <ul style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
              <li>✓ Targeting defended networks with IP whitelisting</li>
              <li>✓ Avoiding network-based detection systems</li>
              <li>✓ Spoofing legitimate service IPs</li>
            </ul>
            <p>
              <strong>When to skip:</strong>
            </p>
            <ul style={{ marginTop: '0.5rem', marginBottom: 0 }}>
              <li>✓ Local network deployment (optional)</li>
              <li>✓ No network monitoring in target environment</li>
              <li>✓ Maximum speed is priority</li>
            </ul>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Select Proxy (Optional):</label>
        <select
          value={selectedProxy || ''}
          onChange={(e) => onSelectProxy(e.target.value || null)}
        >
          <option value="">
            ✓ None - Direct deployment (recommended for most)
          </option>
          {proxies.map((px) => (
            <option key={px.id} value={px.id}>
              ✓ {px.url} ({px.type.toUpperCase()})
            </option>
          ))}
        </select>
      </div>

      {!selectedProxy && (
        <div
          style={{
            padding: '0.8rem',
            marginBottom: '1rem',
            backgroundColor: 'rgba(76, 175, 80, 0.08)',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            borderRadius: '6px',
            fontSize: '0.85rem',
            color: '#a0a0a0',
          }}
        >
          <p style={{ margin: '0 0 0.3rem 0', color: '#4caf50' }}>
            💡 <strong>Running without proxy</strong>
          </p>
          <p style={{ margin: 0 }}>
            This is fine for most scenarios. Only add a proxy if your target has network monitoring.
          </p>
        </div>
      )}

      <button
        className="btn-secondary"
        onClick={() => setShowAddForm(!showAddForm)}
        style={{ width: '100%', marginBottom: '1rem' }}
      >
        {showAddForm ? '✕ Cancel' : '➕ Add Custom Proxy'}
      </button>

      {showAddForm && (
        <div
          style={{
            marginBottom: '1rem',
            padding: '1rem',
            backgroundColor: 'rgba(0, 212, 255, 0.05)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: '6px',
          }}
        >
          <div className="form-group">
            <label>Proxy URL:</label>
            <input
              type="text"
              value={proxyForm.url}
              onChange={(e) => setProxyForm({ ...proxyForm, url: e.target.value })}
              placeholder="e.g., http://proxy.example.com:8080"
            />
            <p style={{ fontSize: '0.8rem', color: '#a0a0a0', margin: '0.5rem 0 0 0' }}>
              Include port number in the URL
            </p>
          </div>
          <div className="form-group">
            <label>Proxy Type:</label>
            <select
              value={proxyForm.type}
              onChange={(e) => setProxyForm({ ...proxyForm, type: e.target.value })}
            >
              <option value="http">HTTP (most common)</option>
              <option value="https">HTTPS (encrypted)</option>
              <option value="socks5">SOCKS5 (advanced)</option>
            </select>
            <p style={{ fontSize: '0.8rem', color: '#a0a0a0', margin: '0.5rem 0 0 0' }}>
              {proxyForm.type === 'http' && 'Standard HTTP proxy - compatible with most systems'}
              {proxyForm.type === 'https' && 'Encrypted proxy connection - best for sensitive networks'}
              {proxyForm.type === 'socks5' && 'SOCKS5 protocol - works with any traffic type'}
            </p>
          </div>
          <button
            className="btn-primary"
            onClick={handleAddProxy}
            style={{ width: '100%' }}
          >
            ✓ Add Proxy Configuration
          </button>
        </div>
      )}
    </div>
  );
}
