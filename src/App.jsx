import React, { useState, useEffect, useCallback, useRef } from 'react';
import FileUpload from './components/FileUpload';
import PayloadGenerator from './components/PayloadGenerator';
import FingerprintSelector from './components/FingerprintSelector';
import ProxyManager from './components/ProxyManager';
import OutputDisplay from './components/OutputDisplay';
import OneClickInstaller from './components/OneClickInstaller';
import PersistencePayload from './components/PersistencePayload';
import RecommendationCard from './components/RecommendationCard';
import apiService from './services/apiService';
import './App.css';

// Error Component with auto-dismiss functionality
function ErrorAlert({ error, onDismiss, type = 'error' }) {
  useEffect(() => {
    if (!error) return;

    const timer = setTimeout(() => {
      onDismiss();
    }, 6000); // Auto-dismiss after 6 seconds

    return () => clearTimeout(timer);
  }, [error, onDismiss]);

  if (!error) return null;

  return (
    <div className={`error-alert error-alert-${type}`}>
      <div className="error-alert-content">
        <span className="error-alert-icon">
          {type === 'error' && '⚠️'}
          {type === 'warning' && '⚡'}
          {type === 'info' && 'ℹ️'}
        </span>
        <div className="error-alert-text">
          <div className="error-alert-title">
            {type === 'error' && 'Error'}
            {type === 'warning' && 'Warning'}
            {type === 'info' && 'Info'}
          </div>
          <div className="error-alert-message">{error}</div>
        </div>
      </div>
      <button
        className="error-alert-close"
        onClick={onDismiss}
        aria-label="Close alert"
      >
        ✕
      </button>
    </div>
  );
}

export default function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [techniques, setTechniques] = useState([]);
  const [fingerprints, setFingerprints] = useState([]);
  const [proxies, setProxies] = useState([]);
  const [selectedTechnique, setSelectedTechnique] = useState('base64');
  const [selectedFingerprint, setSelectedFingerprint] = useState(null);
  const [selectedProxy, setSelectedProxy] = useState(null);
  const [obfuscationLevel, setObfuscationLevel] = useState('high');
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [errorType, setErrorType] = useState('error');
  const [options, setOptions] = useState({
    add_comments: false,
    add_noise: false,
  });
  const [mode, setMode] = useState('standard');  // 'standard', 'one-click', or 'persistent'

  // Abort controllers for fetch cancellation (prevent memory leaks)
  const abortControllersRef = useRef({
    techniques: new AbortController(),
    fingerprints: new AbortController(),
    proxies: new AbortController(),
    payload: new AbortController(),
  });

  // Cleanup function to cancel pending requests
  useEffect(() => {
    return () => {
      Object.values(abortControllersRef.current).forEach(controller => {
        controller.abort();
      });
    };
  }, []);

  // Initialize data on mount
  useEffect(() => {
    fetchTechniques();
    fetchFingerprints();
    fetchProxies();
  }, []);

  // Utility function to extract error message from API service response
  const getErrorMessage = useCallback((errorResponse) => {
    if (typeof errorResponse === 'object' && errorResponse.error) {
      return errorResponse.error;
    }
    return 'An unexpected error occurred';
  }, []);

  // Dismiss error alert
  const dismissError = useCallback(() => {
    setError(null);
    setErrorType('error');
  }, []);

  const fetchTechniques = useCallback(async () => {
    try {
      const controller = new AbortController();
      abortControllersRef.current.techniques = controller;

      const response = await apiService.fetchTechniques(controller.signal);

      if (response.success) {
        if (response.data && response.data.length > 0) {
          setTechniques(response.data);
          setSelectedTechnique(response.data[0]);
        } else {
          setError('No techniques available from server');
          setErrorType('warning');
        }
      } else {
        const message = getErrorMessage(response.error);
        setError(message);
        setErrorType(response.error?.isTimeout ? 'warning' : 'error');
        console.error('Failed to fetch techniques:', response.error);
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        setError('Unexpected error occurred while fetching techniques');
        setErrorType('error');
        console.error('Failed to fetch techniques:', err);
      }
    }
  }, [getErrorMessage]);

  const fetchFingerprints = useCallback(async () => {
    try {
      const controller = new AbortController();
      abortControllersRef.current.fingerprints = controller;

      const response = await apiService.fetchFingerprints(controller.signal);

      if (response.success) {
        if (response.data) {
          setFingerprints(response.data);
        }
      } else {
        console.warn('Failed to fetch fingerprints:', getErrorMessage(response.error));
        // Don't set error for optional fingerprints - just log warning
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        console.warn('Unexpected error occurred while fetching fingerprints:', err);
      }
    }
  }, [getErrorMessage]);

  const fetchProxies = useCallback(async () => {
    try {
      const controller = new AbortController();
      abortControllersRef.current.proxies = controller;

      const response = await apiService.fetchProxies(controller.signal);

      if (response.success) {
        if (response.data) {
          setProxies(response.data);
        }
      } else {
        console.warn('Failed to fetch proxies:', getErrorMessage(response.error));
        // Don't set error for optional proxies - just log warning
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        console.warn('Unexpected error occurred while fetching proxies:', err);
      }
    }
  }, [getErrorMessage]);

  const handleFileUpload = useCallback(async (file) => {
    dismissError();
    setLoading(true);

    if (!file) {
      setError('No file selected');
      setErrorType('error');
      setLoading(false);
      return;
    }

    // Validate file size (limit to 10MB)
    const MAX_FILE_SIZE = 10 * 1024 * 1024;
    if (file.size > MAX_FILE_SIZE) {
      setError(`File too large. Maximum size is 10MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB`);
      setErrorType('error');
      setLoading(false);
      return;
    }

    try {
      const controller = new AbortController();
      abortControllersRef.current.payload = controller;

      const response = await apiService.uploadFile(file, controller.signal);

      if (response.success) {
        if (response.data?.file_id && response.data?.filename) {
          setUploadedFile({
            id: response.data.file_id,
            name: response.data.filename,
            size: response.data.size,
          });
          dismissError();
        } else {
          setError('Invalid response from server');
          setErrorType('error');
        }
      } else {
        const message = getErrorMessage(response.error);
        setError(message);
        setErrorType(response.error?.isTimeout ? 'warning' : 'error');
        console.error('File upload failed:', response.error);
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        setError('Unexpected error occurred during file upload');
        setErrorType('error');
        console.error('File upload failed:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [dismissError, getErrorMessage]);

  const handleGeneratePayload = useCallback(async () => {
    if (!uploadedFile) {
      setError('Please upload a file first');
      setErrorType('warning');
      return;
    }

    if (!selectedTechnique) {
      setError('Please select an encoding technique');
      setErrorType('warning');
      return;
    }

    dismissError();
    setLoading(true);

    try {
      const controller = new AbortController();
      abortControllersRef.current.payload = controller;

      const response = await apiService.generatePayload(
        {
          file_id: uploadedFile.id,
          technique: selectedTechnique,
          obfuscation: obfuscationLevel,
          fingerprint_id: selectedFingerprint,
          proxy_id: selectedProxy,
          options: options,
        },
        controller.signal
      );

      if (response.success) {
        if (response.data?.payload) {
          setPayload({
            id: response.data.output_id || null,
            content: response.data.payload,
            size: response.data.size || 0,
            technique: response.data.technique || selectedTechnique,
          });
          dismissError();
        } else {
          setError('No payload returned from server');
          setErrorType('error');
        }
      } else {
        const message = getErrorMessage(response.error);
        setError(message);
        setErrorType(response.error?.isTimeout ? 'warning' : 'error');
        console.error('Payload generation failed:', response.error);
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        setError('Unexpected error occurred during payload generation');
        setErrorType('error');
        console.error('Payload generation failed:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [uploadedFile, selectedTechnique, obfuscationLevel, selectedFingerprint, selectedProxy, options, dismissError, getErrorMessage]);

  const handleAddProxy = useCallback(async (proxyUrl, proxyType) => {
    if (!proxyUrl || !proxyType) {
      setError('Proxy URL and type are required');
      setErrorType('warning');
      return null;
    }

    try {
      const controller = new AbortController();
      abortControllersRef.current.proxies = controller;

      const response = await apiService.addProxy(proxyUrl, proxyType, controller.signal);

      if (response.success) {
        if (response.data?.id) {
          await fetchProxies();
          return response.data.id;
        } else {
          setError('Invalid response when adding proxy');
          setErrorType('error');
          return null;
        }
      } else {
        const message = getErrorMessage(response.error);
        setError(message);
        setErrorType(response.error?.isTimeout ? 'warning' : 'error');
        console.error('Failed to add proxy:', response.error);
        return null;
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        setError('Unexpected error occurred while adding proxy');
        setErrorType('error');
        console.error('Failed to add proxy:', err);
      }
      return null;
    }
  }, [fetchProxies, getErrorMessage]);

  const handleCreateFingerprint = useCallback(async (name, config) => {
    if (!name || !config) {
      setError('Fingerprint name and configuration are required');
      setErrorType('warning');
      return null;
    }

    try {
      const controller = new AbortController();
      abortControllersRef.current.fingerprints = controller;

      const response = await apiService.createFingerprint(name, config, controller.signal);

      if (response.success) {
        if (response.data?.id) {
          await fetchFingerprints();
          return response.data.id;
        } else {
          setError('Invalid response when creating fingerprint');
          setErrorType('error');
          return null;
        }
      } else {
        const message = getErrorMessage(response.error);
        setError(message);
        setErrorType(response.error?.isTimeout ? 'warning' : 'error');
        console.error('Failed to create fingerprint:', response.error);
        return null;
      }
    } catch (err) {
      if (err.code !== 'ERR_CANCELED') {
        setError('Unexpected error occurred while creating fingerprint');
        setErrorType('error');
        console.error('Failed to create fingerprint:', err);
      }
      return null;
    }
  }, [fetchFingerprints, getErrorMessage]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🔐 SC-Generator</h1>
          <p>Advanced VBS Encryption & Obfuscation Tool</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <ErrorAlert
            error={error}
            type={errorType}
            onDismiss={dismissError}
          />

          <div className="layout">
            <div className="sidebar">
              <section className="panel">
                <h2>📁 File Upload</h2>
                <FileUpload
                  onUpload={handleFileUpload}
                  uploadedFile={uploadedFile}
                  loading={loading}
                />
              </section>

              <section className="panel">
                <h2>⚙️ Mode Selection</h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.8rem' }}>
                  <button
                    className={`btn-secondary ${mode === 'standard' ? 'active' : ''}`}
                    onClick={() => setMode('standard')}
                    style={{
                      backgroundColor: mode === 'standard' ? 'rgba(0, 212, 255, 0.3)' : 'rgba(0, 212, 255, 0.05)',
                      fontSize: '0.9rem',
                    }}
                  >
                    🎯 Standard
                  </button>
                  <button
                    className={`btn-secondary ${mode === 'one-click' ? 'active' : ''}`}
                    onClick={() => setMode('one-click')}
                    style={{
                      backgroundColor: mode === 'one-click' ? 'rgba(0, 212, 255, 0.3)' : 'rgba(0, 212, 255, 0.05)',
                      fontSize: '0.9rem',
                    }}
                  >
                    ⚡ One-Click
                  </button>
                  <button
                    className={`btn-secondary ${mode === 'persistent' ? 'active' : ''}`}
                    onClick={() => setMode('persistent')}
                    style={{
                      backgroundColor: mode === 'persistent' ? 'rgba(0, 212, 255, 0.3)' : 'rgba(0, 212, 255, 0.05)',
                      fontSize: '0.9rem',
                    }}
                  >
                    🔐 Persistent
                  </button>
                </div>
              </section>

              {mode === 'standard' && (
                <>
                  <RecommendationCard mode="standard" />
                  <section className="panel">
                    <h2>🎯 Encoding Technique</h2>
                    <PayloadGenerator
                      techniques={techniques}
                      selectedTechnique={selectedTechnique}
                      onTechniqueChange={setSelectedTechnique}
                      obfuscationLevel={obfuscationLevel}
                      onObfuscationChange={setObfuscationLevel}
                      options={options}
                      onOptionsChange={setOptions}
                    />
                  </section>
                </>
              )}

              {mode === 'standard' && (
                <>
                  <section className="panel">
                    <h2>🔑 Fingerprinting</h2>
                    <FingerprintSelector
                      fingerprints={fingerprints}
                      selectedFingerprint={selectedFingerprint}
                      onSelectFingerprint={setSelectedFingerprint}
                      onCreateFingerprint={handleCreateFingerprint}
                    />
                  </section>

                  <section className="panel">
                    <h2>🌐 Proxy Settings</h2>
                    <ProxyManager
                      proxies={proxies}
                      selectedProxy={selectedProxy}
                      onSelectProxy={setSelectedProxy}
                      onAddProxy={handleAddProxy}
                    />
                  </section>

                  <button
                    className="btn-generate"
                    onClick={handleGeneratePayload}
                    disabled={!uploadedFile || loading}
                  >
                    {loading ? '⏳ Generating...' : '✨ Generate Payload'}
                  </button>
                </>
              )}

              {mode === 'one-click' && (
                <>
                  <RecommendationCard mode="one-click" />
                  <section className="panel">
                    <OneClickInstaller
                      uploadedFile={uploadedFile}
                      loading={loading}
                      onGenerate={(result) => {
                        setPayload({
                          id: result.output_id,
                          content: result.payload,
                          filename: result.filename,
                          size: result.size,
                          technique: 'one-click',
                        });
                      }}
                    />
                  </section>
                </>
              )}

              {mode === 'persistent' && (
                <>
                  <RecommendationCard mode="persistent" />
                  <section className="panel">
                    <PersistencePayload
                      uploadedFile={uploadedFile}
                      loading={loading}
                      onGenerate={(result) => {
                        setPayload({
                          id: result.output_id,
                          content: result.payload,
                          size: result.size,
                          technique: 'persistent',
                        });
                      }}
                    />
                  </section>
                </>
              )}
            </div>

            <div className="main-content">
              <section className="panel full-height">
                <h2>📊 Output</h2>
                <OutputDisplay
                  payload={payload}
                  loading={loading}
                />
              </section>
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>SC-Generator v1.0 | For authorized security research only</p>
      </footer>
    </div>
  );
}
