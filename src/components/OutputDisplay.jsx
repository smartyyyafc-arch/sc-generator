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
              gridTemplateColumns: '1fr 1fr 1fr',
              gap: '1rem',
              marginBottom: '1rem',
            }}
          >
            <div
              style={{
                padding: '1rem',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: '6px',
              }}
            >
              <p style={{ color: '#00d4ff', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                📌 Technique
              </p>
              <p style={{ color: '#a0a0a0', fontWeight: 'bold' }}>
                {payload.technique?.toUpperCase()}
              </p>
            </div>
            <div
              style={{
                padding: '1rem',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: '6px',
              }}
            >
              <p style={{ color: '#00d4ff', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                📏 Payload Size
              </p>
              <p style={{ color: '#a0a0a0', fontWeight: 'bold' }}>
                {(payload.size / 1024).toFixed(2)} KB
              </p>
            </div>
            <div
              style={{
                padding: '1rem',
                backgroundColor:
                  payload.size / 1024 < 20
                    ? 'rgba(76, 175, 80, 0.08)'
                    : payload.size / 1024 < 30
                    ? 'rgba(255, 183, 77, 0.08)'
                    : 'rgba(244, 67, 54, 0.08)',
                border:
                  payload.size / 1024 < 20
                    ? '1px solid rgba(76, 175, 80, 0.3)'
                    : payload.size / 1024 < 30
                    ? '1px solid rgba(255, 183, 77, 0.3)'
                    : '1px solid rgba(244, 67, 54, 0.3)',
                borderRadius: '6px',
              }}
            >
              <p
                style={{
                  color:
                    payload.size / 1024 < 20
                      ? '#4caf50'
                      : payload.size / 1024 < 30
                      ? '#ffb74d'
                      : '#ef5350',
                  fontSize: '0.85rem',
                  marginBottom: '0.3rem',
                }}
              >
                ✓ Size Status
              </p>
              <p style={{ color: '#a0a0a0', fontWeight: 'bold' }}>
                {payload.size / 1024 < 20
                  ? '✓ Optimal'
                  : payload.size / 1024 < 30
                  ? '⚠ Good'
                  : '⚠ Large'}
              </p>
            </div>
          </div>

          {payload.size / 1024 < 20 && (
            <div
              style={{
                padding: '0.8rem',
                marginBottom: '1rem',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                border: '1px solid rgba(76, 175, 80, 0.3)',
                borderRadius: '6px',
                color: '#4caf50',
                fontSize: '0.85rem',
              }}
            >
              ✓ <strong>Perfect size!</strong> Payload is under 20 KB - optimal for deployment
            </div>
          )}

          {payload.size / 1024 >= 20 && payload.size / 1024 < 30 && (
            <div
              style={{
                padding: '0.8rem',
                marginBottom: '1rem',
                backgroundColor: 'rgba(255, 183, 77, 0.1)',
                border: '1px solid rgba(255, 183, 77, 0.3)',
                borderRadius: '6px',
                color: '#ffb74d',
                fontSize: '0.85rem',
              }}
            >
              💡 <strong>Good size.</strong> Payload is under 30 KB - acceptable for most deployments
            </div>
          )}

          {payload.size / 1024 >= 30 && (
            <div
              style={{
                padding: '0.8rem',
                marginBottom: '1rem',
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                border: '1px solid rgba(244, 67, 54, 0.3)',
                borderRadius: '6px',
                color: '#ef5350',
                fontSize: '0.85rem',
              }}
            >
              ⚠ <strong>Large payload.</strong> Consider using lower obfuscation level or simpler technique for smaller size
            </div>
          )}

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
              marginTop: '1.5rem',
              padding: '1rem',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: '6px',
            }}
          >
            <p style={{ margin: '0 0 0.8rem 0', color: '#4caf50', fontWeight: 'bold' }}>
              ✓ Payload Generated Successfully
            </p>

            <div style={{ fontSize: '0.85rem', color: '#a0a0a0', lineHeight: '1.6' }}>
              <p style={{ margin: '0.5rem 0' }}>
                <strong>📋 Quick Summary:</strong>
              </p>
              <ul style={{ margin: '0.5rem 0 1rem 1.5rem', paddingLeft: 0 }}>
                <li>Payload size: {(payload.size / 1024).toFixed(2)} KB</li>
                <li>Technique: {payload.technique?.toUpperCase() || 'Standard'}</li>
                <li>Status: {payload.size / 1024 < 20 ? '✓ Optimal' : 'Ready for deployment'}</li>
              </ul>

              <p style={{ margin: '0.5rem 0' }}>
                <strong>🚀 Next Steps:</strong>
              </p>
              <ol style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                <li>Click "Download" to save the payload file</li>
                <li>Transfer to target system or share via your preferred method</li>
                <li>Execute the payload (double-click or run in console)</li>
                <li>Installation will complete silently in background</li>
              </ol>

              <p style={{ margin: '1rem 0 0.5rem 0' }}>
                <strong>💡 Pro Tips:</strong>
              </p>
              <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                <li>Smaller payloads are faster to transfer and less likely to trigger size-based detection</li>
                <li>Consider your target's network bandwidth when choosing encoding technique</li>
                <li>For large files (&gt;30MB), use lower obfuscation levels</li>
                <li>Test payload on similar system first if possible</li>
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
