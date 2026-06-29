import React, { useState } from 'react';
import axios from 'axios';

export default function OutputDisplay({ payload, loading }) {
  const [copied, setCopied] = useState(false);

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
      const response = await axios.get(`http://localhost:5000/api/download/${payload.id}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payload_${payload.id}.vbs`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleViewSource = async () => {
    if (!payload?.id) return;

    try {
      const response = await axios.get(`http://localhost:5000/api/preview/${payload.id}`);
      alert('Payload Preview:\n\n' + response.data.content.substring(0, 500) + '...');
    } catch (err) {
      console.error('Preview failed:', err);
    }
  };

  return (
    <div className="output-container">
      {loading && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '1rem', color: '#a0a0a0' }}>Generating payload...</p>
        </div>
      )}

      {!loading && !payload && (
        <div className="empty-state">
          <p style={{ fontSize: '1.2rem' }}>📊 Output Preview</p>
          <p>Upload a file and click "Generate Payload" to see results here</p>
        </div>
      )}

      {!loading && payload && (
        <>
          <div className="output-controls">
            <button className="btn-primary" onClick={handleCopy}>
              {copied ? '✓ Copied!' : '📋 Copy Payload'}
            </button>
            <button className="btn-primary" onClick={handleDownload}>
              💾 Download
            </button>
            <button className="btn-secondary" onClick={handleViewSource}>
              👁️ Preview
            </button>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '1rem',
              marginBottom: '1rem',
            }}
          >
            <div>
              <p style={{ color: '#00d4ff', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                📌 Technique
              </p>
              <p style={{ color: '#a0a0a0' }}>{payload.technique?.toUpperCase()}</p>
            </div>
            <div>
              <p style={{ color: '#00d4ff', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                📏 Size
              </p>
              <p style={{ color: '#a0a0a0' }}>
                {(payload.size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>

          <p style={{ color: '#a0a0a0', fontSize: '0.85rem', marginBottom: '0.8rem' }}>
            Payload Preview (First 30 lines):
          </p>

          <div className="code-preview">
            {payload.content
              .split('\n')
              .slice(0, 30)
              .map((line, idx) => (
                <div key={idx}>{line || ' '}</div>
              ))}
            {payload.content.split('\n').length > 30 && (
              <div style={{ color: '#666' }}>
                ... ({payload.content.split('\n').length - 30} more lines)
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: '1rem',
              padding: '0.8rem',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: '6px',
              color: '#4caf50',
              fontSize: '0.9rem',
            }}
          >
            ✓ Payload generated successfully. Ready for deployment.
          </div>
        </>
      )}
    </div>
  );
}
