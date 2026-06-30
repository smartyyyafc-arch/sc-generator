import React, { useState } from 'react';

export default function ProxyManager({
  proxies,
  selectedProxy,
  onSelectProxy,
  onAddProxy,
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [testingProxy, setTestingProxy] = useState(null);
  const [proxyForm, setProxyForm] = useState({
    url: '',
    tags: [],
    notes: '',
  });

  const handleAddProxy = async () => {
    if (!proxyForm.url) {
      alert('Please enter a proxy URL');
      return;
    }

    try {
      const response = await fetch('/api/proxies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: proxyForm.url,
          tags: proxyForm.tags,
          notes: proxyForm.notes,
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setProxyForm({ url: '', tags: [], notes: '' });
          setShowAddForm(false);
          // Refresh proxies
          onAddProxy(proxyForm.url, proxyForm.tags);
        } else {
          alert(`Error: ${data.error}`);
        }
      }
    } catch (error) {
      alert(`Failed to add proxy: ${error.message}`);
    }
  };

  const handleTestProxy = async (proxyId) => {
    setTestingProxy(proxyId);
    try {
      const response = await fetch(`/api/proxies/${proxyId}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timeout: 10 })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Test result: ${data.success ? 'PASSED' : 'FAILED'}\n${data.message}`);
      }
    } catch (error) {
      alert(`Test failed: ${error.message}`);
    } finally {
      setTestingProxy(null);
    }
  };

  const handleFetchStats = async () => {
    try {
      const response = await fetch('/api/proxies');
      if (response.ok) {
        const data = await response.json();
        setStatistics(data.statistics);
        setShowStats(!showStats);
      }
    } catch (error) {
      alert(`Failed to fetch statistics: ${error.message}`);
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <label>Select Proxy (Optional):</label>
          <button
            className="btn-secondary"
            onClick={handleFetchStats}
            style={{
              padding: '0.4rem 0.8rem',
              fontSize: '0.85rem',
            }}
          >
            {showStats ? '✕ Hide Stats' : '📊 Stats'}
          </button>
        </div>
        <select
          value={selectedProxy || ''}
          onChange={(e) => onSelectProxy(e.target.value || null)}
        >
          <option value="">
            ✓ None - Direct deployment (recommended for most)
          </option>
          {proxies.map((px) => (
            <option key={px.id} value={px.id}>
              ✓ {px.url} ({px.proxy_type.toUpperCase()})
            </option>
          ))}
        </select>

        {showStats && statistics && (
          <div
            style={{
              marginTop: '1rem',
              padding: '1rem',
              backgroundColor: 'rgba(76, 175, 80, 0.08)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: '6px',
              fontSize: '0.85rem',
            }}
          >
            <p style={{ margin: '0 0 0.5rem 0', color: '#4caf50', fontWeight: 'bold' }}>
              📊 Proxy Statistics
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8rem' }}>
              <div>Total: {statistics.total_proxies}</div>
              <div>Active: {statistics.active_proxies}</div>
              <div>Tested: {statistics.tested_proxies}</div>
              <div>Passed: {statistics.passed_tests}</div>
            </div>
            {Object.keys(statistics.by_type || {}).length > 0 && (
              <div style={{ marginTop: '0.5rem' }}>
                <p style={{ margin: '0.3rem 0', fontWeight: 'bold' }}>By Type:</p>
                {Object.entries(statistics.by_type).map(([type, count]) => (
                  <div key={type} style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>
                    {type.toUpperCase()}: {count}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {!selectedProxy && (
        <div
          style={{
            padding: '0.8rem',
            marginBottom: '1rem',
            marginTop: '0.5rem',
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

      {selectedProxy && (
        <div style={{ marginTop: '0.5rem' }}>
          {proxies.find((p) => p.id === selectedProxy) && (
            <button
              className="btn-secondary"
              onClick={() => handleTestProxy(selectedProxy)}
              disabled={testingProxy === selectedProxy}
              style={{
                width: '100%',
                padding: '0.5rem',
                marginBottom: '0.5rem',
                backgroundColor: testingProxy === selectedProxy ? 'rgba(76, 175, 80, 0.3)' : 'rgba(76, 175, 80, 0.1)',
              }}
            >
              {testingProxy === selectedProxy ? '⏳ Testing...' : '✓ Test Proxy'}
            </button>
          )}
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
              placeholder="e.g., http://proxy.example.com:8080 or socks5://user:pass@socks.example.com:1080"
            />
            <p style={{ fontSize: '0.8rem', color: '#a0a0a0', margin: '0.5rem 0 0 0' }}>
              Supports: HTTP, HTTPS, SOCKS4, SOCKS5. Use user:pass@host:port for authentication.
            </p>
          </div>

          <div className="form-group">
            <label>Tags (Optional):</label>
            <input
              type="text"
              value={proxyForm.tags.join(', ')}
              onChange={(e) => setProxyForm({
                ...proxyForm,
                tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
              })}
              placeholder="e.g., corporate, secure, test"
            />
            <p style={{ fontSize: '0.8rem', color: '#a0a0a0', margin: '0.5rem 0 0 0' }}>
              Comma-separated tags for organizing proxies
            </p>
          </div>

          <div className="form-group">
            <label>Notes (Optional):</label>
            <textarea
              value={proxyForm.notes}
              onChange={(e) => setProxyForm({ ...proxyForm, notes: e.target.value })}
              placeholder="e.g., Corporate proxy, requires authentication"
              rows="3"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <button
              className="btn-primary"
              onClick={handleAddProxy}
            >
              ✓ Add Proxy
            </button>
            <button
              className="btn-secondary"
              onClick={() => setShowAddForm(false)}
            >
              ✕ Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
