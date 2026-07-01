import React, { useState } from 'react';
import { GlobeIcon, PlusIcon, XIcon, InfoIcon } from './Icons';

export default function ProxyManager({
  proxies,
  selectedProxy,
  onSelectProxy,
  onAddProxy,
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [proxyForm, setProxyForm] = useState({ url: '', type: 'http' });

  const handleAddProxy = async () => {
    if (!proxyForm.url) return;
    const id = await onAddProxy(proxyForm.url, proxyForm.type);
    if (id) {
      setProxyForm({ url: '', type: 'http' });
      setShowAddForm(false);
    }
  };

  return (
    <div>
      <h2><GlobeIcon /> Proxy Settings</h2>

      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Configuration</span>
          <button
            className="btn-secondary"
            onClick={() => setShowInfo(!showInfo)}
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
          >
            <InfoIcon size={12} /> {showInfo ? 'Hide' : 'Info'}
          </button>
        </label>

        {showInfo && (
          <div className="info-box neutral" style={{ marginBottom: '0.75rem', fontSize: '0.75rem' }}>
            <p style={{ marginBottom: '0.375rem' }}>
              Proxies modify network signatures to evade IP-based detection.
            </p>
            <p style={{ color: 'var(--text-muted)', margin: 0 }}>
              Optional for most scenarios. Only needed for defended networks.
            </p>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Select Proxy (Optional)</label>
        <select
          value={selectedProxy || ''}
          onChange={(e) => onSelectProxy(e.target.value || null)}
        >
          <option value="">None - Direct deployment</option>
          {proxies.map((px) => (
            <option key={px.id} value={px.id}>
              {px.url} ({px.type.toUpperCase()})
            </option>
          ))}
        </select>
      </div>

      <button
        className="btn-secondary"
        onClick={() => setShowAddForm(!showAddForm)}
        style={{ width: '100%' }}
      >
        {showAddForm ? <><XIcon size={14} /> Cancel</> : <><PlusIcon size={14} /> Add Proxy</>}
      </button>

      {showAddForm && (
        <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-default)' }}>
          <div className="form-group">
            <label>URL</label>
            <input
              type="text"
              value={proxyForm.url}
              onChange={(e) => setProxyForm({ ...proxyForm, url: e.target.value })}
              placeholder="http://proxy.example.com:8080"
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Type</label>
            <select
              value={proxyForm.type}
              onChange={(e) => setProxyForm({ ...proxyForm, type: e.target.value })}
            >
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
              <option value="socks5">SOCKS5</option>
            </select>
          </div>
          <button className="btn-primary" onClick={handleAddProxy} style={{ width: '100%', marginTop: '0.75rem' }}>
            Add Proxy
          </button>
        </div>
      )}
    </div>
  );
}
