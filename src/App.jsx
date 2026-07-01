import React, { useState, useEffect, Suspense, lazy } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import PayloadGenerator from './components/PayloadGenerator';
import FingerprintSelector from './components/FingerprintSelector';
import ProxyManager from './components/ProxyManager';
import OutputDisplay from './components/OutputDisplay';
import RecommendationCard from './components/RecommendationCard';
import { ShieldIcon, TargetIcon, ZapIcon, LockIcon, LayersIcon } from './components/Icons';
import { API_BASE } from './config';
import './App.css';

const OneClickInstaller = lazy(() => import('./components/OneClickInstaller'));
const PersistencePayload = lazy(() => import('./components/PersistencePayload'));
const CombinedMode = lazy(() => import('./components/CombinedMode'));

const MODES = [
  { id: 'standard', label: 'Standard', icon: TargetIcon },
  { id: 'one-click', label: 'One-Click', icon: ZapIcon },
  { id: 'persistent', label: 'Persistent', icon: LockIcon },
  { id: 'combined', label: 'Combined', icon: LayersIcon },
];

export default function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [techniques, setTechniques] = useState([]);
  const [techniqueMetadata, setTechniqueMetadata] = useState({});
  const [fingerprints, setFingerprints] = useState([]);
  const [proxies, setProxies] = useState([]);
  const [selectedTechnique, setSelectedTechnique] = useState('base64');
  const [selectedFingerprint, setSelectedFingerprint] = useState(null);
  const [selectedProxy, setSelectedProxy] = useState(null);
  const [obfuscationLevel, setObfuscationLevel] = useState('high');
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [options, setOptions] = useState({ add_comments: false, add_noise: false });
  const [mode, setMode] = useState('standard');

  useEffect(() => {
    fetchTechniques();
    fetchFingerprints();
    fetchProxies();
  }, []);

  const fetchTechniques = async () => {
    try {
      const response = await axios.get(`${API_BASE}/techniques`);
      setTechniques(response.data.techniques);
      setTechniqueMetadata(response.data.metadata || {});
      setSelectedTechnique(response.data.techniques[0]);
    } catch (err) {
      setError('Failed to fetch techniques');
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
        options,
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
      const response = await axios.post(`${API_BASE}/proxies`, { url: proxyUrl, type: proxyType });
      fetchProxies();
      return response.data.id;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add proxy');
    }
  };

  const handleCreateFingerprint = async (name, config) => {
    try {
      const response = await axios.post(`${API_BASE}/fingerprints`, { name, config });
      fetchFingerprints();
      return response.data.id;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create fingerprint');
    }
  };

  const suspenseFallback = (
    <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
      Loading...
    </div>
  );

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-brand">
            <div className="header-logo">
              <ShieldIcon size={20} />
            </div>
            <div>
              <h1>SC-Generator</h1>
              <p>VBS Payload Encryption & Obfuscation</p>
            </div>
          </div>
          <span className="header-version">v2.0</span>
        </div>
      </header>

      <nav className="mode-tabs">
        <div className="mode-tabs-inner">
          {MODES.map(({ id, label, icon: ModeIcon }) => (
            <button
              key={id}
              className={`mode-tab ${mode === id ? 'active' : ''}`}
              onClick={() => setMode(id)}
            >
              <ModeIcon size={16} />
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main className="app-main">
        <div className="container">
          {error && <div className="error-banner">{error}</div>}

          <div className="layout">
            <div className="sidebar">
              <section className="panel">
                <FileUpload
                  onUpload={handleFileUpload}
                  uploadedFile={uploadedFile}
                  loading={loading}
                />
              </section>

              {mode === 'standard' && (
                <>
                  <RecommendationCard mode="standard" />
                  <section className="panel">
                    <PayloadGenerator
                      techniques={techniques}
                      techniqueMetadata={techniqueMetadata}
                      selectedTechnique={selectedTechnique}
                      onTechniqueChange={setSelectedTechnique}
                      obfuscationLevel={obfuscationLevel}
                      onObfuscationChange={setObfuscationLevel}
                      options={options}
                      onOptionsChange={setOptions}
                    />
                  </section>
                  <section className="panel">
                    <FingerprintSelector
                      fingerprints={fingerprints}
                      selectedFingerprint={selectedFingerprint}
                      onSelectFingerprint={setSelectedFingerprint}
                      onCreateFingerprint={handleCreateFingerprint}
                    />
                  </section>
                  <section className="panel">
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
                    {loading ? 'Generating...' : 'Generate Payload'}
                  </button>
                </>
              )}

              {mode === 'one-click' && (
                <>
                  <RecommendationCard mode="one-click" />
                  <section className="panel">
                    <Suspense fallback={suspenseFallback}>
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
                    </Suspense>
                  </section>
                </>
              )}

              {mode === 'persistent' && (
                <>
                  <RecommendationCard mode="persistent" />
                  <section className="panel">
                    <Suspense fallback={suspenseFallback}>
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
                    </Suspense>
                  </section>
                </>
              )}

              {mode === 'combined' && (
                <section className="panel">
                  <Suspense fallback={suspenseFallback}>
                    <CombinedMode
                      uploadedFile={uploadedFile}
                      onGenerate={(result) => {
                        setPayload({
                          id: result.output_id,
                          content: result.payload,
                          size: result.size,
                          technique: 'combined',
                          stages: result.stages,
                          metadata: result.metadata,
                        });
                      }}
                    />
                  </Suspense>
                </section>
              )}
            </div>

            <div className="main-content">
              <section className="panel full-height">
                <OutputDisplay payload={payload} loading={loading} />
              </section>
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        SC-Generator v2.0 &middot; For authorized security research only
      </footer>
    </div>
  );
}
