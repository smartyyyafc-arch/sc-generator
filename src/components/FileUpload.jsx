import React, { useState, useRef } from 'react';
import { UploadIcon, FileIcon, CheckIcon } from './Icons';
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
        `Invalid file type. Allowed: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`
      );
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const handleDragLeave = () => setDragOver(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0 && validateFile(e.dataTransfer.files[0])) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0 && validateFile(e.target.files[0])) {
      onUpload(e.target.files[0]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
  };

  return (
    <div>
      <h2><UploadIcon /> File Upload</h2>
      <div
        className={`file-upload-area ${dragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        tabIndex={0}
        onKeyDown={handleKeyDown}
        role="button"
        aria-label="Upload file area"
      >
        <div className="upload-icon">
          <UploadIcon size={40} />
        </div>
        <p>Drag & drop your MSI/EXE file here</p>
        <p style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>or</p>
        <input
          type="file"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          id="file-input"
          ref={fileInputRef}
          accept=".exe,.msi,.dll,.bat,.cmd,.vbs,.ps1"
          disabled={loading}
        />
        <label htmlFor="file-input" className="upload-browse">
          Browse files
        </label>
      </div>

      {validationError && (
        <div className="status-message error" style={{ marginTop: '0.5rem' }}>
          {validationError}
        </div>
      )}

      {uploadedFile && (
        <div className="file-info">
          <p style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
            <FileIcon size={14} />
            <strong>{uploadedFile.name}</strong>
          </p>
          <p>{formatFileSize(uploadedFile.size)}</p>
          <p className="file-ready" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <CheckIcon size={14} /> Ready
          </p>
        </div>
      )}
    </div>
  );
}
