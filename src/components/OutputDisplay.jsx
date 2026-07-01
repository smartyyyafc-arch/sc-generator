import React, { useState } from 'react';
import axios from 'axios';
import { CopyIcon, DownloadIcon, EyeIcon, CheckIcon, CodeIcon, TerminalIcon } from './Icons';
import { API_BASE } from '../config';

export default function OutputDisplay({ payload, loading }) {
  const [copied, setCopied] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [previewContent, setPreviewContent] = useState(null);

  const showStatus = (message, type = 'info') => {
    setStatusMessage({ message, type });
    setTimeout(() => setStatusMessage(null), 4000);
  };

  const handleCopy = () => {
    if (payload?.content) {
      navigator.clipboard.writeText(payload.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
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
      link.setAttribute('download', `payload_${payload.id}.vbs`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      showStatus('Download failed. Please try again.', 'error');
    }
  };

  const handlePreview = async () => {
    if (!payload?.id) return;
    try {
      const response = await axios.get(`${API_BASE}/preview/${payload.id}`);
      setPreviewContent(response.data.content.substring(0, 500) + '...');
    } catch (err) {
      showStatus('Preview failed.', 'error');
    }
  };

  const sizeKB = payload ? payload.size / 1024 : 0;
  const sizeStatus = sizeKB < 20 ? 'success' : sizeKB < 30 ? 'warning' : 'danger';
  const sizeLabel = sizeKB < 20 ? 'Optimal' : sizeKB < 30 ? 'Good' : 'Large';

  return (
    <div className="output-container">
      <h2><TerminalIcon /> Output</h2>

      {statusMessage && (
        <div className={`status-message ${statusMessage.type}`}>
          {statusMessage.message}
        </div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="spinner" />
          <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Generating payload...
          </p>
        </div>
      )}

      {!loading && !payload && (
        <div className="empty-state">
          <CodeIcon size={48} />
          <p>Upload a file and generate a payload to see output here</p>
        </div>
      )}

      {!loading && payload && (
        <>
          <div className="output-controls">
            <button className="btn-primary" onClick={handleCopy}>
              {copied ? <><CheckIcon size={14} /> Copied</> : <><CopyIcon size={14} /> Copy</>}
            </button>
            <button className="btn-primary" onClick={handleDownload}>
              <DownloadIcon size={14} /> Download
            </button>
            <button className="btn-secondary" onClick={handlePreview}>
              <EyeIcon size={14} /> Preview
            </button>
          </div>

          {previewContent && (
            <div style={{
              padding: '0.75rem',
              marginBottom: '0.75rem',
              background: 'var(--bg-primary)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.75rem',
              fontFamily: "'JetBrains Mono', monospace",
              whiteSpace: 'pre-wrap',
              color: 'var(--text-muted)',
              maxHeight: '200px',
              overflowY: 'auto',
              border: '1px solid var(--border-default)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: '0.75rem' }}>
                  Server Preview
                </span>
                <button
                  className="btn-secondary"
                  onClick={() => setPreviewContent(null)}
                  style={{ padding: '0.15rem 0.4rem', fontSize: '0.6875rem' }}
                >
                  Close
                </button>
              </div>
              {previewContent}
            </div>
          )}

          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Technique</div>
              <div className="stat-value">{payload.technique?.toUpperCase()}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Payload Size</div>
              <div className="stat-value">{sizeKB.toFixed(1)} KB</div>
            </div>
            <div className="stat-card" style={{
              borderColor: `var(--${sizeStatus}-border)`,
            }}>
              <div className="stat-label">Size Status</div>
              <div className="stat-value" style={{ color: `var(--${sizeStatus})` }}>
                {sizeLabel}
              </div>
            </div>
          </div>

          <div style={{
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
            marginBottom: '0.5rem',
            fontWeight: 500,
          }}>
            Code Preview (first 30 lines)
          </div>

          <div className="code-preview">
            {payload.content
              .split('\n')
              .slice(0, 30)
              .map((line, idx) => (
                <div key={idx}>{line || ' '}</div>
              ))}
            {payload.content.split('\n').length > 30 && (
              <div style={{ color: 'var(--text-muted)', opacity: 0.5, marginTop: '0.5rem' }}>
                ... ({payload.content.split('\n').length - 30} more lines)
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
