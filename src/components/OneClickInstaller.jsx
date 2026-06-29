import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export default function OneClickInstaller({ uploadedFile, loading, onGenerate }) {
  const [styles, setStyles] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState('polymorphic');
  const [fileType, setFileType] = useState('vbs');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [payload, setPayload] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchStyles();
  }, []);

  const fetchStyles = async () => {
    try {
      const response = await axios.get(`${API_BASE}/one-click-styles`);
      setStyles(response.data.styles);
    } catch (err) {
      console.error('Failed to fetch styles', err);
    }
  };

  const handleGenerate = async () => {
    if (!uploadedFile) {
      alert('Please upload a file first');
      return;
    }

    setGenerating(true);

    try {
      const response = await axios.post(`${API_BASE}/generate-one-click`, {
        file_id: uploadedFile.id,
        obfuscation_style: selectedStyle,
        file_type: fileType,
      });

      setPayload({
        id: response.data.output_id,
        filename: response.data.filename,
        content: response.data.payload,
        instructions: response.data.instructions,
        size: response.data.size,
      });

      onGenerate?.(response.data);
    } catch (err) {
      alert(err.response?.data?.error || 'Generation failed');
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
      link.setAttribute('download', payload.filename);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
    } catch (err) {
      console.error('Download failed:', err);
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
      <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>⚡ One-Click Installer</h3>

      <div className="form-group">
        <label>Obfuscation Style:</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          {Object.entries(styles).map(([key, desc]) => (
            <div
              key={key}
              className={`fingerprint-card ${selectedStyle === key ? 'selected' : ''}`}
              onClick={() => setSelectedStyle(key)}
              style={{ cursor: 'pointer' }}
            >
              <div className="fingerprint-name">{key.toUpperCase()}</div>
              <div className="fingerprint-desc">{desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Output Format:</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          {[
            { value: 'vbs', label: 'VBS Script', desc: 'Windows VBScript file' },
            { value: 'bat', label: 'Batch File', desc: 'Batch executable wrapper' },
          ].map((opt) => (
            <div
              key={opt.value}
              className={`fingerprint-card ${fileType === opt.value ? 'selected' : ''}`}
              onClick={() => setFileType(opt.value)}
              style={{ cursor: 'pointer' }}
            >
              <div className="fingerprint-name">{opt.label}</div>
              <div className="fingerprint-desc">{opt.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <button
        className="btn-primary"
        onClick={handleGenerate}
        disabled={!uploadedFile || generating}
        style={{ width: '100%' }}
      >
        {generating ? '⏳ Generating...' : '✨ Generate One-Click Installer'}
      </button>

      <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#a0a0a0' }}>
        <p>
          💡 <strong>One-Click Installer:</strong> User double-clicks the file and installation
          completes silently in background with zero visible output.
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
          <h4 style={{ color: '#4caf50', marginTop: 0 }}>✓ Installer Generated</h4>

          <div style={{ marginBottom: '1rem' }}>
            <p>
              <strong>Filename:</strong> <code>{payload.filename}</code>
            </p>
            <p>
              <strong>Size:</strong> {(payload.size / 1024).toFixed(2)} KB
            </p>
          </div>

          <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#a0a0a0' }}>
            <p>
              <strong>Installation Instructions:</strong>
            </p>
            <pre style={{ whiteSpace: 'pre-wrap', color: '#4caf50' }}>{payload.instructions}</pre>
          </div>

          <div style={{ display: 'flex', gap: '0.8rem', flexWrap: 'wrap' }}>
            <button className="btn-primary" onClick={handleDownload}>
              💾 Download Installer
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
