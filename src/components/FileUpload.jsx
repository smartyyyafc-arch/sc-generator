import React, { useState } from 'react';

export default function FileUpload({ onUpload, uploadedFile, loading }) {
  const [dragOver, setDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onUpload(files[0]);
    }
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onUpload(files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes, k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div>
      <div
        className={`file-upload-area ${dragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p>📁 Drag & drop your MSI/EXE file here</p>
        <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>or click to browse</p>
        <input
          type="file"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          id="file-input"
          disabled={loading}
        />
        <label htmlFor="file-input" style={{ cursor: 'pointer' }}>
          Click here
        </label>
      </div>

      {uploadedFile && (
        <div className="file-info">
          <p>
            <strong>✓ File Uploaded:</strong> {uploadedFile.name}
          </p>
          <p>
            <strong>Size:</strong> {formatFileSize(uploadedFile.size)}
          </p>
          <p>
            <strong>Status:</strong> <span style={{ color: '#4caf50' }}>Ready</span>
          </p>
        </div>
      )}
    </div>
  );
}
