import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import PayloadGenerator from './components/PayloadGenerator';
import FingerprintSelector from './components/FingerprintSelector';
import ProxyManager from './components/ProxyManager';
import OutputDisplay from './components/OutputDisplay';
import './App.css';

const API_BASE = 'http://localhost:5000/api';

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
  const [options, setOptions] = useState({
    add_comments: false,
    add_noise: false,
  });

  useEffect(() => {
    fetchTechniques();
    fetchFingerprints();
    fetchProxies();
  }, []);

  const fetchTechniques = async () => {
    try {
      const response = await axios.get(`${API_BASE}/techniques`);
      setTechniques(response.data.techniques);
      setSelectedTechnique(response.data.techniques[0]);
    } catch (err) {
      setError('Failed to fetch techniques');
      console.error(err);
    }
  };

  const fetchFingerprints = async () => {
    try {
      const response = await axios.get(`${API_BASE}/fingerprints`);
      setFingerprints(response.data.fingerprints);
    } catch (err) {
      console.error('Failed to fetch fingerprints', err);
    }
  };

  const fetchProxies = async () => {
    try {
      const response = await axios.get(`${API_BASE}/proxies`);
      setProxies(response.data.proxies);
    } catch (err) {
      console.error('Failed to fetch proxies', err);
    }
  };

  const handleFileUpload = async (file) => {
    setError(null);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadedFile({
        id: response.data.file_id,
        name: response.data.filename,
        size: response.data.size,
      });

      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePayload = async () => {
    if (!uploadedFile) {
      setError('Please upload a file first');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/generate-payload`, {
        file_id: uploadedFile.id,
        technique: selectedTechnique,
        obfuscation: obfuscationLevel,
        fingerprint_id: selectedFingerprint,
        proxy_id: selectedProxy,
        options: options,
      });

      setPayload({
        id: response.data.output_id,
        content: response.data.payload,
        size: response.data.size,
        technique: response.data.technique,
      });

      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Payload generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAddProxy = async (proxyUrl, proxyType) => {
    try {
      const response = await axios.post(`${API_BASE}/proxies`, {
        url: proxyUrl,
        type: proxyType,
      });
      fetchProxies();
      return response.data.id;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add proxy');
    }
  };

  const handleCreateFingerprint = async (name, config) => {
    try {
      const response = await axios.post(`${API_BASE}/fingerprints`, {
        name,
        config,
      });
      fetchFingerprints();
      return response.data.id;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create fingerprint');
    }
  };

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
          {error && <div className="error-banner">{error}</div>}

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
