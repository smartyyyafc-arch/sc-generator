import React, { useState, useRef } from 'react';
import { ALLOWED_FILE_EXTENSIONS } from '../config';

export default function FileUpload({ onUpload, uploadedFile, loading }) {
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    const fileName = file.name.toLowerCase();
    const hasValidExtension = ALLOWED_FILE_EXTENSIONS.some((ext) =>
      fileName.endsWith(ext)
    );
    if (!hasValidExtension) {
      setValidationError(
        `Invalid file type. Allowed extensions: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`
      );
      return false;
    }
    setValidationError(null);
    return true;
  };

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
      if (validateFile(files[0])) {
        onUpload(files[0]);
      }
    }
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      if (validateFile(files[0])) {
        onUpload(files[0]);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div>
      <div
        className={`file-upload-area ${dragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        tabIndex={0}
        onKeyDown={handleKeyDown}
        role="button"
        aria-label="Upload file area. Press Enter or Space to browse files."
      >
        <p>📁 Drag & drop your MSI/EXE file here</p>
        <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>or click to browse</p>
        <input
          type="file"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          id="file-input"
          ref={fileInputRef}
          accept=".exe,.msi"
          disabled={loading}
        />
        <label htmlFor="file-input" style={{ cursor: 'pointer' }}>
          Click here
        </label>
      </div>

      {validationError && (
        <div className="status-message error" style={{ marginTop: '0.5rem' }}>
          {validationError}
        </div>
      )}

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
